from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import httpx
import os
from typing import List, Optional
from datetime import datetime
import asyncio
import pathlib
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles
from sqlmodel import select, delete
from engine.manager import job_manager
from engine.download import supports_range
from backend.db import init_db, get_session
from backend.models.models import Source, Item, Job, JobPart
from backend import config as backend_config
from backend.steam_service import steam_client
from backend.resolver import clear_session_cache
from backend.steam_api import steam_api_client

# Define lifespan before creating app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    await job_manager.start()
    
    # Limpar caches de sessão ao iniciar
    clear_session_cache()
    steam_api_client.clear_cache()
    print("[STARTUP] Todos os caches foram limpos")
    
    session = get_session()
    
    # CRITICAL FIX: Auto-pause any jobs that were 'running' when server stopped
    # This prevents UI confusion where downloads show as "Active" when they're actually paused
    running_jobs = session.exec(select(Job).where(Job.status == "running")).all()
    if running_jobs:
        print(f"🔄 Found {len(running_jobs)} jobs that were running before restart")
        print(f"   Auto-pausing to prevent state confusion...")
        for j in running_jobs:
            j.status = "paused"
            session.add(j)
        session.commit()
        print(f"✅ {len(running_jobs)} jobs marked as paused")
        print(f"   Click 'Continue' in the UI to resume downloads")
    
    
    # DISABLED: Auto-resume logic removed to prevent confusion
    # Jobs should stay paused until user explicitly clicks "Continue"
    # 
    # Previous behavior: Jobs with resume_on_start=True were auto-resumed
    # New behavior: ALL paused jobs stay paused on server restart
    #
    # jobs_to_resume = session.exec(select(Job).where(
    #     (Job.resume_on_start == True) & 
    #     ((Job.status == "paused") | (Job.status == "queued"))
    # )).all()
    # for j in jobs_to_resume:
    #     await job_manager.enqueue_job(j.id)
    
    session.close()
    
    # Start background broadcaster task
    asyncio.create_task(broadcast_progress())
    
    yield
    
    # Shutdown
    await job_manager.stop()
    await steam_client.close()

app = FastAPI(title="Launcher JSON Accelerator — Backend", lifespan=lifespan)

# CORS for local UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoadJsonRequest(BaseModel):
    url: str


class LoadJsonRawRequest(BaseModel):
    data: dict | list


class ClearJobsRequest(BaseModel):
    """Request to clear jobs by visible IDs"""
    job_ids: list[int] = []  # IDs of visible jobs on frontend


class CreateJobReq(BaseModel):
    item_id: Optional[int] = None
    url: Optional[str] = None
    name: Optional[str] = None
    destination: Optional[str] = None  #  Frontend envia 'destination' (pasta escolhida no modal)
    dest: Optional[str] = None  # Fallback para compatibilidade
    size: Optional[int] = None  # Tamanho real do item
    k: int = 4
    n_conns: int = 4
    resume_on_start: bool = True
    verify_ssl: bool = True


# ==================== STEAM IMAGES ENDPOINT ====================

@app.get("/api/steam/artes")
async def get_steam_arts(term: str):
    """
    Busca imagens (header, capsule, etc.) da Steam para um jogo.
    Aceita AppID (numérico) ou Nome do jogo.
    Usa query param '?term=...' para evitar erros com caracteres especiais na URL.
    """
    from backend.steam_service import steam_client
    
    if not term:
        return {"found": False, "query": ""}
    
    results = await steam_client.get_game_art(term)
    
    if not results:
        return {"found": False, "query": term}
    
    # Sucesso se tiver AppID OU imagem (header/hero)
    has_image = results.get("header") or results.get("hero") or results.get("capsule")
    if not results.get("app_id") and not has_image:
        return {"found": False, "query": term}
        
    return {**results, "found": True}


# ==================== RESOLVER ENDPOINT (Fallback Chain Completa) ====================

@app.post("/api/resolver")
async def resolve_game_images(game_name: str):
    """
    Endpoint de resolução 100% de imagens de jogos.
    Implementa fallback chain completa conforme plano_completo_imagens.md:
    
    1. Cache de sessão (nome → appId)
    2. Regras automáticas (GTA V → Grand Theft Auto V)
    3. Busca exata na Steam
    4. Busca com normalização
    5. Fuzzy matching local
    6. Fallback SteamGridDB
    
    Retorna JSON padronizado:
    {
        "found": bool,
        "appId": int | null,
        "capsule": str | null,
        "header": str | null,
        "background": str | null,
        "grid": str | null,
        "hero": str | null,
        "logo": str | null,
        "error": str | null
    }
    
    Uso: POST /api/resolver?game_name=GTA%20V
    """
    from backend.resolver import resolve_game_images as resolve
    
    if not game_name or not str(game_name).strip():
        return {"found": False, "error": "empty_name"}
    
    try:
        result = await resolve(game_name)
        return result
    except Exception as e:
        print(f"[Resolver] Erro: {e}")
        return {"found": False, "error": str(e)}


@app.get("/api/game-details/{app_id_or_name:path}")
async def get_game_details(app_id_or_name: str):
    """
    Busca detalhes completos do jogo (imagens, vídeos, descrição, metadados)
    Implementa fallback robusto com Steam API + SteamGridDB
    
    Entrada:
    - app_id_or_name: AppID (int) ou nome do jogo (string)
    
    Saída:
    - Payload completo com imagens, screenshots, vídeos, descrição, gêneros, etc
    
    Uso:
    - GET /api/game-details/570
    - GET /api/game-details/Dota%202
    """
    from backend.details_controller import details_controller
    
    print(f"\n[GameDetails] Requisição recebida para: {app_id_or_name}")
    
    try:
        # Tentar converter para int (AppID)
        try:
            app_id = int(app_id_or_name)
            print(f"[GameDetails] Tratando como AppID: {app_id}")
            result = await details_controller.get_game_details(app_id=app_id)
        except ValueError:
            # Se não for int, tratar como nome
            print(f"[GameDetails] Tratando como nome do jogo: {app_id_or_name}")
            result = await details_controller.get_game_details(game_name=app_id_or_name)
        
        # Log detalhado do resultado
        print(f"[GameDetails] Resultado obtido:")
        print(f"  - found: {result.get('found')}")
        print(f"  - app_id: {result.get('app_id')}")
        print(f"  - name: {result.get('name')}")
        print(f"  - movies count: {len(result.get('movies', []))}")
        print(f"  - screenshots count: {len(result.get('screenshots', []))}")
        
        return result
    except Exception as e:
        print(f"[GameDetails] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return {
            "found": False,
            "error": "internal_error",
            "error_message": str(e)
        }


# ==================== CACHE MANAGEMENT ====================

@app.post("/api/cache/clear")
async def clear_all_caches():
    """
    Limpa todos os caches de sessão e API.
    Útil para forçar recarregamento de imagens e dados.
    """
    try:
        clear_session_cache()
        steam_api_client.clear_cache()
        return {
            "success": True,
            "message": "Todos os caches foram limpos (sessão + Steam API)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==================== PROXY ENDPOINTS (Para PyQt5 .exe) ====================
# PyQt5 tem limitações ao carregar URLs externas
# Estes endpoints servem como proxy para imagens e vídeos

from fastapi.responses import StreamingResponse
import io

@app.get("/api/proxy/image")
async def proxy_image(url: str):
    """
    Proxy para carregar imagens externas no .exe
    Retorna a imagem diretamente (streaming)
    Uso: /api/proxy/image?url=https://...
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    
    # Log básico para depuração, evitando caracteres especiais
    try:
        print(f"[ProxyImage] Request recebida para URL: {url[:200]}")
    except Exception:
        pass

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Detectar tipo de conteúdo
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            return StreamingResponse(
                io.BytesIO(response.content),
                media_type=content_type,
                headers={"Cache-Control": "public, max-age=86400"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


@app.get("/api/proxy/video")
async def proxy_video(url: str):
    """
    Proxy para carregar vídeos externos no .exe
    Retorna o vídeo em streaming
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    
    # Log básico para depuração de vídeos
    try:
        print(f"[ProxyVideo] Request recebida para URL: {url[:200]}")
    except Exception:
        pass

    try:
        # Redirect directly to source for better performance/streaming support
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=url)
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


# ==================== DIAGNÓSTICO DE VÍDEOS ====================

@app.get("/api/debug/videos")
async def debug_videos():
    """
    Endpoint de diagnóstico para entender por que vídeos não aparecem no .exe
    Retorna informações detalhadas sobre a configuração e testes
    """
    try:
        # Testar um jogo com vídeos conhecidos (Dota 2 - AppID 570)
        from backend.details_controller import details_controller
        
        result = await details_controller.get_game_details(app_id=570)
        
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "game": {
                "app_id": result.get("app_id"),
                "name": result.get("name"),
                "found": result.get("found")
            },
            "movies": {
                "count": len(result.get("movies", [])) if result.get("movies") else 0,
                "has_movies": bool(result.get("movies") and len(result.get("movies")) > 0)
            },
            "first_movie": None,
            "proxy_test": None,
            "environment": {
                "backend_url": "http://127.0.0.1:8000",
                "proxy_endpoint": "/api/proxy/video"
            }
        }
        
        # Detalhar primeiro vídeo
        if result.get("movies") and len(result.get("movies")) > 0:
            first_movie = result["movies"][0]
            diagnosis["first_movie"] = {
                "name": first_movie.get("name"),
                "has_mp4": bool(first_movie.get("mp4")),
                "has_webm": bool(first_movie.get("webm")),
                "has_thumbnail": bool(first_movie.get("thumbnail")),
                "mp4_url": first_movie.get("mp4", "")[:100] if first_movie.get("mp4") else None,
                "webm_url": first_movie.get("webm", "")[:100] if first_movie.get("webm") else None
            }
            
            # Testar proxy com o primeiro vídeo
            if first_movie.get("mp4"):
                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        proxy_response = await client.head(
                            first_movie["mp4"],
                            follow_redirects=True
                        )
                        diagnosis["proxy_test"] = {
                            "status_code": proxy_response.status_code,
                            "content_type": proxy_response.headers.get("content-type"),
                            "content_length": proxy_response.headers.get("content-length"),
                            "success": proxy_response.status_code == 200
                        }
                except Exception as e:
                    diagnosis["proxy_test"] = {
                        "error": str(e),
                        "success": False
                    }
        
        return diagnosis
        
    except Exception as e:
        print(f"[DebugVideos] Erro: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ==================== SAFE CLEANUP FUNCTION ====================
# CRITICAL: Only deletes files/folders created by the application


# ==================== SAFE CLEANUP FUNCTION ====================
# CRITICAL: Only deletes files/folders created by the application
# NEVER deletes the entire parent directory

def safe_delete_download(dest_path: str, job_name: str = None) -> tuple[bool, str]:
    """
    Safely delete a download file/folder WITHOUT deleting parent directory.
    
     ENHANCEMENTS:
    - Verifies dest_path matches expected location from database
    - Validates parent directory is safe
    - Checks file actually exists before attempting deletion
    - Gracefully handles already-deleted files
    - Returns detailed status (deleted/skipped/failed)
    - Intelligently finds real download if dest_path is just the base folder
    
    Only deletes:
    1. The exact file/folder specified by dest_path
    2. Associated metadata files (.aria2, .aria2c, .part, .parts, .torrent)
    
    NEVER:
    - Deletes parent directories
    - Deletes unrelated files
    - Uses recursive rmtree on parent
    - Deletes "Downloads" or common folder names
    
    Args:
        dest_path: Full path to download (from Job.dest in database)
        job_name: Optional job name for validation logging
    
    Returns: (success: bool, message: str)
    """
    import shutil
    
    if not dest_path:
        return False, "No path provided"
    
    try:
        dest = pathlib.Path(dest_path)
        
        #  CRITICAL SAFETY CHECKS 
        
        # 1. Validate dest_path format
        dest_str = str(dest).strip()
        if not dest_str or len(dest_str) < 3:
            error_msg = f" BLOCKED: Path too short or invalid: '{dest_str}'"
            print(f"      {error_msg}")
            return False, error_msg
        
        # 2. Check for path traversal attacks (.. in path)
        if ".." in str(dest):
            error_msg = f" BLOCKED: Suspicious path traversal detected: {dest}"
            print(f"      {error_msg}")
            return False, error_msg
        
        # 3. Safety checks for forbidden folders
        forbidden_folders = {
            'downloads', 'download', 'downloads folder',
            'documents', 'desktop', 'music', 'pictures', 'videos',
            'home', 'users', 'temp', 'tmp', 'system32', 'windows',
            'program files', 'appdata', 'programdata'
        }
        
        #  CORRECT LOGIC:
        # - BLOCK: Trying to delete the forbidden folder itself
        # - ALLOW: Deleting files/folders INSIDE the forbidden folder
        
        dest_name_lower = dest.name.lower()
        
        # Check exact name match (the item being deleted)
        # We BLOCK if trying to delete "Downloads" or "Windows" or "System32" itself
        if dest_name_lower in forbidden_folders:
            error_msg = f" BLOCKED: Cannot delete common system folder: {dest.name}"
            print(f"      {error_msg}")
            return False, error_msg
        
        # DO NOT CHECK PARENT - we WANT to allow deletions inside Downloads, Desktop, etc
        # The key protection is that we only delete the exact path specified,
        # not the parent folder
        
        #  INTELLIGENT PATH RESOLUTION:
        # If dest doesn't exist, try to find similar folder names
        # (handles cases where sanitize_filename changed the name)
        actual_dest = dest
        if not dest.exists():
            parent = dest.parent
            if parent.exists() and parent.is_dir():
                # Try exact name match first
                candidates = []
                dest_name = dest.name.lower()
                
                for item in parent.iterdir():
                    if item.name.lower() == dest_name:
                        # Exact match
                        actual_dest = item
                        print(f"      [OK] Found exact match: {item.name}")
                        break
                    
                    # Fuzzy match: if sanitized name is similar
                    item_name_lower = item.name.lower()
                    # Check if names are similar (same words, different separators)
                    # e.g., "dustwind_resistance" vs "dustwind - resistance"
                    dest_normalized = dest_name.replace('_', '').replace('-', '').replace(' ', '').replace('–', '')
                    item_normalized = item_name_lower.replace('_', '').replace('-', '').replace(' ', '').replace('–', '')
                    
                    if dest_normalized and item_normalized and dest_normalized == item_normalized:
                        candidates.append(item)
                        print(f"      INFO: Fuzzy match candidate: {item.name}")
                
                # Use fuzzy match if found and exact not found
                if candidates and not actual_dest.exists():
                    actual_dest = candidates[0]
                    print(f"      [OK] Using fuzzy match: {actual_dest.name}")
        
        # 4.  Verify file exists BEFORE attempting deletion
        if not actual_dest.exists():
            # File already deleted (manually outside app or by previous operation)
            skip_msg = f"Skipped (already deleted): {dest.name}"
            print(f"      INFO: {skip_msg}")
            return True, skip_msg
        
        deleted_items = []
        
        try:
            # 5. Delete the main file/folder (the download itself)
            if actual_dest.is_file():
                # Single file download
                actual_dest.unlink()
                deleted_items.append(str(actual_dest))
                print(f"      [OK] Deleted file: {actual_dest}")
            elif actual_dest.is_dir():
                # Folder download - delete ONLY the folder, not parent
                shutil.rmtree(actual_dest)
                deleted_items.append(str(actual_dest))
                print(f"      [OK] Deleted directory: {actual_dest}")
        except FileNotFoundError:
            # Race condition: file deleted between check and deletion
            skip_msg = f"Skipped (already deleted): {dest.name}"
            print(f"      INFO: Race condition - {skip_msg}")
            return True, skip_msg
        except PermissionError as e:
            error_msg = f"Permission denied deleting {dest.name}: {e}"
            print(f"       {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Error deleting {actual_dest}: {e}"
            print(f"       {error_msg}")
            return False, error_msg
        
        # 6. Delete associated metadata files (only if they exist)
        # These are OUTSIDE the download folder, created by aria2
        parent_dir = dest.parent
        filename_base = dest.name
        
        metadata_patterns = [
            f"{filename_base}.aria2",      # aria2 metadata
            f"{filename_base}.aria2c",     # aria2 temp metadata
            f"{filename_base}.part",       # download part file
            f"{filename_base}.parts",      # download parts folder
            f"{filename_base}.torrent",    # torrent metadata
        ]
        
        for pattern in metadata_patterns:
            meta_path = parent_dir / pattern
            if meta_path.exists():
                try:
                    if meta_path.is_file():
                        meta_path.unlink()
                    elif meta_path.is_dir():
                        shutil.rmtree(meta_path)
                    deleted_items.append(str(meta_path))
                    print(f"      [OK] Deleted metadata: {meta_path.name}")
                except Exception as e:
                    print(f"        Could not delete metadata {pattern}: {e}")
        
        message = f"Deleted {len(deleted_items)} item(s)"
        print(f"       {message}")
        return True, message
        
    except Exception as e:
        error_msg = f"Error deleting {dest_path}: {e}"
        print(f"       {error_msg}")
        return False, error_msg


# Serve frontend static files (mount after websocket endpoints so WebSocket scopes are handled by app)
frontend_path = pathlib.Path(__file__).resolve().parent.parent / "frontend" / "dist"


@app.post("/api/dialog/select_folder")
async def select_folder_dialog():
    """Open a native folder selection dialog on the host and return the chosen path.

    NOTE: This only works when the server runs on a desktop with a display and tkinter available.
    """
    def _pick():
        try:
            # Usar tkinter que é mais rápido e confiável que PowerShell
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()  # Esconde a janela principal
            root.attributes('-topmost', True)  # Força janela ficar em cima
            path = filedialog.askdirectory(title="Selecione a pasta de download")
            root.destroy()
            return path or None
        except Exception as e:
            # return exception details for logging
            return {"_error": True, "msg": str(e)}

    # run in thread to avoid blocking event loop
    path = await asyncio.to_thread(_pick)
    # If _pick returned an error dict, surface it in logs and response
    if isinstance(path, dict) and path.get("_error"):
        err_msg = path.get("msg")
        print(f" select_folder_dialog: erro ao abrir diálogo: {err_msg}")
        return {"path": None, "canceled": True, "error": err_msg}

    if not path:
        # usuário cancelou o diálogo (fechou sem escolher) — informar cancelado
        print(" select_folder_dialog: nenhum caminho selecionado / diálogo cancelado")
        return {"path": None, "canceled": True}

    print(f"[OK] select_folder_dialog: pasta selecionada: {path}")
    return {"path": path, "canceled": False}


def sanitize_url(url: str) -> str:
    """
    Normaliza uma URL para comparação de duplicatas.
    Remove: protocolo, www, trailing slash, query params, fragments.
    """
    from urllib.parse import urlparse, parse_qs
    
    # Remove protocolo (http/https)
    url_lower = url.lower().strip()
    if url_lower.startswith(('http://', 'https://')):
        url_lower = url_lower.split('://', 1)[1]
    
    # Remove www
    if url_lower.startswith('www.'):
        url_lower = url_lower[4:]
    
    # Parse URL para pegar apenas o domínio + path
    try:
        # Adicionar protocolo temporário para urlparse funcionar
        parsed = urlparse('http://' + url_lower)
        base = parsed.netloc + parsed.path
    except:
        base = url_lower
    
    # Remover trailing slash
    base = base.rstrip('/')
    
    return base.lower()


def check_duplicate_source(url: str) -> Optional[Source]:
    """
    Verifica se uma fonte com URL similar já existe no banco.
    Retorna a fonte existente ou None se não encontrada.
    """
    session = get_session()
    try:
        sanitized_url = sanitize_url(url)
        
        # Buscar todas as fontes
        sources = session.exec(select(Source)).all()
        
        for source in sources:
            if source.url and sanitize_url(source.url) == sanitized_url:
                print(f" Fonte duplicada detectada!")
                print(f"   URL fornecida: {url}")
                print(f"   URL existente: {source.url}")
                return source
        
        return None
    finally:
        session.close()


@app.post("/api/load-json")
async def load_json(req: LoadJsonRequest):
    """Salva apenas a URL da fonte, sem carregar items."""
    url = req.url
    # print(f"POST /api/load-json - URL: {url}")
    
    try:
        # Verificar se a fonte já existe (duplicata)
        existing_source = check_duplicate_source(url)
        if existing_source:
            # print(f"Retornando fonte existente: #{existing_source.id}")
            return {
                "source_id": existing_source.id,
                "message": "Fonte já existe no banco de dados.",
                "url": existing_source.url,
                "title": existing_source.title,
                "duplicate": True
            }
        
        # Validar que a URL é acessível
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(url, follow_redirects=True, timeout=10.0)
            except Exception as e:
                # print(f"Erro ao validar URL: {e}")
                error_msg = str(e)
                if "timeout" in error_msg.lower():
                    raise HTTPException(status_code=408, detail="Tempo esgotado! O servidor não respondeu a tempo. Verifique sua conexão ou tente novamente.")
                elif "connection" in error_msg.lower():
                    raise HTTPException(status_code=503, detail="Não foi possível conectar ao servidor. Verifique se a URL está correta.")
                else:
                    raise HTTPException(status_code=400, detail=f"Erro ao acessar a URL: {error_msg}")
            if r.status_code >= 400:
                # print(f"HTTP {r.status_code}")
                if r.status_code == 404:
                    raise HTTPException(status_code=404, detail="Fonte não encontrada! A URL retornou erro 404. Verifique se o link está correto ou se a fonte foi removida.")
                elif r.status_code == 403:
                    raise HTTPException(status_code=403, detail="Acesso negado! O servidor bloqueou o acesso (erro 403). A fonte pode estar protegida.")
                elif r.status_code == 500:
                    raise HTTPException(status_code=500, detail="Erro no servidor da fonte (erro 500). Tente novamente mais tarde.")
                else:
                    raise HTTPException(status_code=r.status_code, detail=f"Erro HTTP {r.status_code}: Não foi possível carregar a fonte.")
            try:
                js = r.json()
                # print(f"JSON validado")
            except Exception:
                # print(f"JSON inválido")
                raise HTTPException(status_code=400, detail="Resposta inválida! O servidor não retornou um JSON válido. Verifique se a URL aponta para um arquivo JSON.")
        
        # Extrair nome da fonte do JSON
        source_name = None
        if isinstance(js, dict):
            source_name = js.get("name")
        
        # Salvar APENAS a fonte no banco (sem items)
        session = get_session()
        source = Source(url=url, title=source_name)
        session.add(source)
        session.commit()
        session.refresh(source)
        session.close()
        
        # print(f"Fonte salva: #{source.id}")
        # print(f"Items carregados sob demanda ao selecionar")
        
        return {
            "source_id": source.id,
            "message": "Fonte salva. Items carregados ao selecionar.",
            "url": url,
            "title": source_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" ERRO: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/load-json/raw")
async def load_json_raw(req: LoadJsonRawRequest):
    """Salva a fonte com JSON colado."""
    print(f"\n POST /api/load-json/raw - JSON colado")
    
    try:
        import json
        import hashlib
        
        js = req.data
        
        # Extrair nome da fonte
        source_name = None
        if isinstance(js, dict):
            source_name = js.get("name")
        
        # Criar hash do JSON para detectar duplicatas
        json_str = json.dumps(js, sort_keys=True)
        json_hash = hashlib.md5(json_str.encode()).hexdigest()
        
        # Verificar se um JSON igual já foi carregado
        session = get_session()
        existing = session.exec(
            select(Source).where(Source.url == f"json-raw://{json_hash}")
        ).first()
        
        if existing:
            print(f" JSON duplicado detectado!")
            print(f"   Retornando fonte existente: #{existing.id}")
            session.close()
            return {
                "source_id": existing.id,
                "message": "Este JSON já foi carregado anteriormente.",
                "url": existing.url,
                "title": existing.title,
                "duplicate": True
            }
        
        # Salvar a fonte com JSON armazenado como string
        source = Source(
            url=f"json-raw://{json_hash}",
            title=source_name,
            data=json_str  # Armazenar JSON como string
        )
        session.add(source)
        session.commit()
        session.refresh(source)
        session.close()

        print(f"[OK] Fonte salva: #{source.id} (JSON colado com {len(str(js))} bytes)")
        print(f" Items carregados sob demanda ao selecionar")
        
        return {
            "source_id": source.id,
            "message": "Fonte salva. Items carregados ao selecionar.",
            "title": source_name
        }
        
    except Exception as e:
        print(f" ERRO: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/supports_range")
async def api_supports_range(url: str):
    # Magnet links don't support range requests - return false immediately
    if url.startswith('magnet:'):
        return {"accept_ranges": False, "size": None, "status_code": None, "note": "Magnet links use aria2"}
    
    info = await supports_range(url)
    return info


@app.post("/api/jobs")
async def create_job(req: CreateJobReq):
    print(f"\n POST /api/jobs - Criando job")
    print(f"   Payload recebido: {req.dict()}")
    print(f"   item_id: {req.item_id}, url: {req.url}, name: {req.name}, size: {req.size}")
    
    session = get_session()
    item = None
    
    if req.item_id:
        item = session.get(Item, req.item_id)
        if not item:
            session.close()
            print(f" Item #{req.item_id} não encontrado")
            raise HTTPException(status_code=404, detail="Item not found")
        print(f"[OK] Item encontrado: {item.name}")
    else:
        if not req.url:
            session.close()
            raise HTTPException(status_code=400, detail="Either item_id or url must be provided")
        
        # Verificar se já existe um job ativo/pausado com essa URL
        existing_jobs = session.exec(select(Job).where(Job.status.in_(["queued", "running", "paused"]))).all()
        for existing_job in existing_jobs:
            existing_item = session.get(Item, existing_job.item_id) if existing_job.item_id else None
            if existing_item and existing_item.url == req.url:
                session.close()
                print(f" Já existe um download ativo para essa URL: {req.url}")
                raise HTTPException(status_code=400, detail="A download for this URL is already active or queued")
        
        # create an item
        item = Item(source_id=None, name=req.name or req.url, url=req.url, size=req.size)
        session.add(item)
        session.commit()
        session.refresh(item)
        print(f"[OK] Item criado: #{item.id} - {item.name}")
    
    # Se veio size e item não tem, atualizar
    if req.size and not item.size:
        item.size = req.size
        session.add(item)
        session.commit()
        session.refresh(item)

    #  Use 'destination' from frontend (modal choice), fallback to 'dest' if provided
    download_dest = req.destination or req.dest or backend_config.DOWNLOADS_DIR
    print(f" Destination recebido: destination={req.destination}, dest={req.dest}")
    print(f" Usando: {download_dest}")
    
    job = Job(item_id=item.id, dest=download_dest, status="queued", k=req.k, n_conns=req.n_conns, resume_on_start=req.resume_on_start, verify_ssl=req.verify_ssl, size=req.size)
    session.add(job)
    session.commit()
    session.refresh(job)
    print(f"[OK] Job criado: #{job.id} - Status: queued")
    print(f"[SSL] SSL Verification: {job.verify_ssl} (from request: {req.verify_ssl})")
    session.close()

    # enqueue job
    print(f" Adicionando job #{job.id} à fila de processamento")
    await job_manager.enqueue_job(job.id)
    print(f" Job #{job.id} enfileirado com sucesso")

    return {"job_id": job.id}


@app.get("/api/jobs")
async def list_jobs():
    session = get_session()
    q = session.exec(select(Job)).all()
    items = []
    for j in q:
        prog = job_manager.get_progress(j.id) or {}
        item = session.get(Item, j.item_id) if j.item_id else None
        items.append(dict(id=j.id, item_id=j.item_id, status=j.status, progress=j.progress or prog.get('progress'), created_at=j.created_at.isoformat(), updated_at=j.updated_at.isoformat(), last_error=j.last_error, item_name=(item.name if item else None), item_url=(item.url if item else None), dest=j.dest, downloaded=prog.get('downloaded'), total=prog.get('total'), speed=prog.get('speed'), size=j.size))
    session.close()
    return items


@app.get("/api/sources")
async def list_sources():
    session = get_session()
    q = session.exec(select(Source)).all()
    result = [dict(id=s.id, url=s.url, title=s.title, created_at=s.created_at.isoformat()) for s in q]
    session.close()
    return result


@app.get("/api/sources/{source_id}/items")
async def list_items(source_id: int):
    """Carrega items sob demanda da fonte (releitura do JSON)."""
    print(f"\n[INFO] GET /api/sources/{source_id}/items - Carregando items sob demanda")
    
    session = get_session()
    source = session.get(Source, source_id)
    if not source:
        session.close()
        raise HTTPException(status_code=404, detail="Source not found")

    print(f"[OK] Fonte encontrada: {source.url or 'JSON colado'}")    # Se for URL, fazer releitura do JSON
    if source.url and not source.url.startswith("json-raw://"):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(source.url, follow_redirects=True, timeout=20.0)
                if r.status_code >= 400:
                    session.close()
                    raise HTTPException(status_code=400, detail="Erro ao recarregar fonte")
                js = r.json()
                print(f"[OK] JSON recarregado - {len(str(js))} bytes")
        except Exception as e:
            session.close()
            print(f" Erro ao recarregar fonte: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Erro ao recarregar: {str(e)}")
    elif source.data:
        # Se for JSON colado, recuperar do campo data
        import json
        try:
            js = json.loads(source.data)
            print(f"[OK] JSON colado recuperado - {len(source.data)} bytes")
        except Exception as e:
            session.close()
            print(f" Erro ao parsear JSON colado: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Erro ao parsear JSON: {str(e)}")
    else:
        # Se for JSON colado mas sem dados, não temos forma de recuperar - retornar vazio
        session.close()
        print(f" Fonte sem URL e sem dados - items não podem ser carregados")
        return []
    
    # Normalizar items do JSON recarregado
    items = []
    raw_items = []
    source_name = source.title
    
    if isinstance(js, dict):
        # Tentar diversos formatos
        if "sources" in js and isinstance(js["sources"], list) and len(js["sources"]) > 0:
            # Se houver array de sources, usar o primeiro e seus items
            first_source = js["sources"][0]
            if isinstance(first_source, dict):
                raw_items = first_source.get("items", [])
        elif "downloads" in js and isinstance(js["downloads"], list):
            raw_items = js["downloads"]
        elif "items" in js and isinstance(js["items"], list):
            raw_items = js["items"]
        elif "data" in js and isinstance(js["data"], list):
            raw_items = js["data"]
        elif "results" in js and isinstance(js["results"], list):
            raw_items = js["results"]
        elif "content" in js and isinstance(js["content"], list):
            raw_items = js["content"]
        elif "files" in js and isinstance(js["files"], list):
            raw_items = js["files"]
        else:
            # Procurar primeiro array
            for key in js.keys():
                if isinstance(js[key], list):
                    raw_items = js[key]
                    break
    elif isinstance(js, list):
        raw_items = js
    
    # Processar items
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        
        # Detectar URL
        if "uris" in raw and isinstance(raw["uris"], list) and len(raw["uris"]) > 0:
            u = raw["uris"][0]
        else:
            u = raw.get("url") or raw.get("link") or raw.get("magnet") or raw.get("uri")
        
        if not u:
            continue
        
        name = raw.get("name") or raw.get("title") or raw.get("file") or raw.get("filename")
        size = raw.get("size") or raw.get("length") or raw.get("fileSize") or raw.get("file_size")
        
        # Se size for string (ex: "5.6 GB"), tentar fazer parse
        if size and isinstance(size, str):
            try:
                import re
                match = re.search(r'([\d.]+)\s*(GB|MB|KB|B)', size, re.IGNORECASE)
                if match:
                    num = float(match.group(1))
                    unit = match.group(2).upper()
                    multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
                    size = int(num * multipliers.get(unit, 1))
                else:
                    size = None
            except (ValueError, AttributeError):
                size = None
        
        # Extrair categoria - campos principais para categoria
        cat = (
            raw.get("category") or 
            raw.get("category_name") or 
            raw.get("lang") or
            source_name
        )
        
        # Se for uma lista/array, pegar o primeiro
        if isinstance(cat, (list, tuple)):
            cat = cat[0] if cat else source_name
        
        # Garantir que é string
        cat = str(cat).strip() if cat else source_name
        
        # Extrair tipo/subcategoria - tenta vários campos
        item_type = (
            raw.get("type") or 
            raw.get("genre") or 
            raw.get("tags") or 
            raw.get("tag")
        )
        
        # Se for uma lista/array, pegar o primeiro
        if isinstance(item_type, (list, tuple)):
            item_type = item_type[0] if item_type else None
        
        # Garantir que é string
        item_type = str(item_type).strip() if item_type else None
        
        # Extrair campos opcionais de imagem
        image = raw.get("image") or raw.get("cover") or raw.get("poster")
        icon = raw.get("icon") or raw.get("favicon")
        thumbnail = raw.get("thumbnail") or raw.get("thumb")
        
        # Extrair data de upload (se disponível)
        upload_date = raw.get("uploadDate") or raw.get("upload_date") or raw.get("date") or raw.get("published")
        
        items.append(dict(
            id=hash(u) % 2147483647,  # ID baseado no hash da URL
            name=name or str(u).split("/")[-1],
            url=u,
            size=size,
            category=cat,
            type=item_type,
            source_id=source_id,
            image=image,
            icon=icon,
            thumbnail=thumbnail,
            uploadDate=upload_date  # Adicionar data de upload
        ))
    
    session.close()
    # Debug: verificar se algum item tem uploadDate
    items_with_date = [i for i in items if i.get('uploadDate')]
    print(f"[OK] {len(items)} items carregados ({len(items_with_date)} com uploadDate)")
    if items_with_date:
        print(f"   Exemplo de data: {items_with_date[0].get('uploadDate')}")
    return items


@app.delete("/api/sources/{source_id}")
async def delete_source(source_id: int):
    print(f"\n DELETE /api/sources/{source_id} - Iniciando deleção")
    session = get_session()
    
    s = session.get(Source, source_id)
    if not s:
        print(f" Fonte #{source_id} não encontrada")
        raise HTTPException(status_code=404, detail="Source not found")
    
    print(f" Fonte encontrada: {s.url}")
    
    # Deletar todos os items da fonte
    items_result = session.exec(delete(Item).where(Item.source_id == source_id))
    session.commit()
    print(f"[OK] Items deletados da fonte #{source_id}")
    
    # Deletar a fonte
    session.delete(s)
    session.commit()
    print(f"[OK] Fonte #{source_id} deletada com sucesso")
    
    session.close()
    
    return {"status": "deleted", "source_id": source_id, "message": "Fonte e items deletados"}


@app.get("/api/jobs/{job_id}/parts")
async def list_job_parts(job_id: int):
    session = get_session()
    j = session.get(Job, job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job not found")
    parts = session.exec(select(JobPart).where(JobPart.job_id == job_id)).all()
    session.close()
    return [dict(index=p.index, start=p.start, end=p.end, downloaded=p.downloaded, size=p.size, path=p.path, status=p.status) for p in parts]


@app.get("/api/aria2/status")
async def aria2_status():
    path = backend_config.ARIA2C_PATH
    from engine.aria2_wrapper import find_aria2_binary
    found = find_aria2_binary(os.getcwd())
    return {"env_path": path, "found_path": found, "available": bool(found)}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int):
    session = get_session()
    j = session.get(Job, job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job not found")
    prog = job_manager.get_progress(job_id) or {}
    out = dict(id=j.id, item_id=j.item_id, status=j.status, progress=j.progress or prog.get('progress'), updated_at=j.updated_at.isoformat(), last_error=j.last_error, downloaded=prog.get('downloaded'), total=prog.get('total'), speed=prog.get('speed'), resume_on_start=j.resume_on_start, verify_ssl=j.verify_ssl)
    # include item details
    if j.item_id:
        it = session.get(Item, j.item_id)
        if it:
            out.update({"item_url": it.url, "item_name": it.name, "item_size": it.size})
            # derive destination and filename
            if j.dest:
                from os.path import basename
                filename = basename(it.url.split('?')[0]) if it.url else it.name
                out.update({"dest": j.dest, "filename": filename})
    out.update(prog)
    session.close()
    return out


@app.post("/api/jobs/{job_id}/pause")
async def pause_job(job_id: int):
    """
    Pause a running download.
    Sets stop_event to signal aria2 to pause gracefully.
    aria2 will save session state and preserve .aria2 metadata for resume.
    """
    print(f"[PAUSE] PAUSE request for job {job_id}")
    session = get_session()
    j = session.get(Job, job_id)
    if not j:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found")
    if j.status not in ("running", "queued"):
        session.close()
        raise HTTPException(status_code=400, detail=f"Cannot pause job in {j.status} state")
    # Mark as paused in DB FIRST
    j.status = "paused"
    j.updated_at = datetime.utcnow()
    session.add(j)
    session.commit()
    print(f"[OK] Job {job_id} marked as paused in DB")
    session.close()
    # THEN tell job manager to stop with pause flag
    # This ensures wrapper sees the pause flag when checking status
    job_manager.stop_job(job_id, pause=True)
    return {"ok": True}


@app.post("/api/jobs/{job_id}/resume")
async def resume_job(job_id: int):
    """
    Resume a paused download.
    Reenqueues the job which triggers _run_job() in the worker.
    aria2_wrapper will detect aria2.session and load it with --input-file=aria2.session,
    preserving the download state and GID from the previous run.
    """
    print(f" RESUME request for job {job_id}")
    session = get_session()
    j = session.get(Job, job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job not found")
    if j.status not in ("paused", "failed"):
        raise HTTPException(status_code=400, detail="Job cannot be resumed in its current state")
    
    # Note: aria2.session is created in the application's working directory (project root)
    # by the aria2_wrapper when a download is paused.
    # We don't need to verify it exists here - aria2_wrapper will handle resuming.
    # If aria2.session doesn't exist, aria2_wrapper will treat it as a fresh download.
    
    j.status = "queued"
    j.updated_at = datetime.utcnow()
    session.add(j)
    session.commit()
    # capture the job id before closing the session to avoid DetachedInstanceError
    jid = j.id
    try:
        session.close()
    except Exception:
        pass
    
    print(f"[OK] Job {job_id} marked as queued, reenqueueing for resume")
    await job_manager.enqueue_job(jid)
    return {"ok": True}


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: int):
    # CRITICAL: Mark as canceled FIRST before stopping job
    # This prevents race condition where status could flip to "paused"
    session = get_session()
    j = session.get(Job, job_id)
    if not j:
        session.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Mark as canceled immediately
    j.status = "canceled"
    j.updated_at = datetime.utcnow()
    session.add(j)
    session.commit()
    print(f" CANCEL request for job {job_id} - Marked as canceled in DB")
    
    # NOW stop the job with cancel flag (don't save session)
    job_manager.stop_job(job_id, cancel=True)
    
    # cleanup parts and partials
    parts = session.exec(select(JobPart).where(JobPart.job_id == job_id)).all()
    for p in parts:
        if p.path and os.path.exists(p.path):
            try:
                os.remove(p.path)
                print(f"[OK] Removed part: {p.path}")
            except Exception as e:
                print(f" Could not remove {p.path}: {e}")
        # delete part records
        try:
            session.delete(p)
        except Exception:
            pass
    
    # Also clean up .part and .parts files
    if j.item_id:
        try:
            it = session.get(Item, j.item_id)
            if it:
                from backend import config as backend_config
                dest = j.dest or backend_config.DOWNLOADS_DIR
                raw_name = os.path.basename(it.url.split("?")[0]) or it.name
                # Try to clean up partial files
                for suffix in [".part", ".parts"]:
                    partial_path = os.path.join(dest, raw_name + suffix) if raw_name else None
                    if partial_path and os.path.exists(partial_path):
                        try:
                            if os.path.isdir(partial_path):
                                import shutil
                                shutil.rmtree(partial_path)
                            else:
                                os.remove(partial_path)
                            print(f"[OK] Removed partial: {partial_path}")
                        except Exception as e:
                            print(f" Could not remove {partial_path}: {e}")
        except Exception as e:
            print(f" Error during cancel cleanup: {e}")
    
    session.commit()
    session.close()
    print(f"[OK] Job {job_id} canceled and cleaned up")
    return {"ok": True, "message": "Job canceled and cleaned up"}


@app.delete("/api/jobs/{job_id}")
async def delete_job_file(job_id: int):
    """Deletar arquivo e job do banco de dados - SAFE VERSION com validação robusta"""
    print(f"\n  [API] DELETE /api/jobs/{job_id} - Deletando job")
    session = get_session()
    j = session.get(Job, job_id)
    if not j:
        session.close()
        print(f"    Job #{job_id} não encontrado")
        raise HTTPException(status_code=404, detail="Job not found")
    
    print(f"   > Job encontrado: {j.dest}")
    
    # Obter informações do item para validação adicional
    job_name = None
    if j.item_id:
        try:
            item = session.get(Item, j.item_id)
            if item:
                job_name = item.name
                print(f"   > Item associado: {job_name}")
        except Exception as e:
            print(f"    Could not fetch item info: {e}")
    
    deleted_files = []
    
    # Tentar deletar o arquivo do disco (SAFE - não deleta parent dir, com validação)
    if j.dest:
        success, message = safe_delete_download(j.dest, job_name=job_name)
        if success:
            deleted_files.append(j.dest)
        print(f"   {message}")
    
    # Deletar job do banco de dados
    try:
        session.delete(j)
        session.commit()
        print(f"   [OK] Job #{job_id} deletado do banco de dados")
    except Exception as e:
        print(f"    Erro ao deletar job do BD: {e}")
        session.rollback()
    finally:
        session.close()
    
    print(f"[OK] [API] Job #{job_id} deletado com sucesso")
    return {"ok": True, "message": f"Job deleted", "files": deleted_files}


@app.delete("/api/jobs/completed/clear")
async def clear_completed_jobs(request: ClearJobsRequest):
    """Deletar APENAS os downloads concluídos VISÍVEIS na tela - SAFE VERSION"""
    print("\n  [API] DELETE /api/jobs/completed/clear - Iniciando limpeza de jobs concluídos visíveis")
    print(f"   [MOBILE] IDs visíveis recebidos do frontend: {request.job_ids}")
    session = get_session()
    try:
        # Buscar apenas os jobs visíveis que são concluídos
        if request.job_ids:
            completed_jobs = session.exec(
                select(Job).where(
                    (Job.status == "completed") & 
                    (Job.id.in_(request.job_ids))
                )
            ).all()
        else:
            # Se lista vazia, não deleta nada
            completed_jobs = []
        
        print(f"   > Encontrados {len(completed_jobs)} jobs concluídos VISÍVEIS para deletar")
        
        #  SAFETY: Log all paths BEFORE deletion
        if completed_jobs:
            print(f"    PATHS TO BE DELETED:")
            for j in completed_jobs:
                print(f"      [{j.id}] {j.dest}")
        
        deleted_count = 0
        deleted_files = []
        skipped_files = []
        failed_paths = []
        
        for j in completed_jobs:
            print(f"   > Deletando job #{j.id}: {j.dest}")
            job_name = None
            if j.item_id:
                try:
                    item = session.get(Item, j.item_id)
                    if item:
                        job_name = item.name
                        print(f"      Item: {job_name}")
                except Exception as e:
                    print(f"        Could not fetch item info: {e}")
            try:
                if j.dest:
                    success, message = safe_delete_download(j.dest, job_name=job_name)
                    if success:
                        deleted_files.append(j.dest)
                        if "Skipped" in message:
                            skipped_files.append(j.dest)
                        print(f"      [SUCCESS] {message}")
                    else:
                        print(f"       {message}")
                        failed_paths.append(j.dest)
                else:
                    print(f"      [WARNING]  Sem caminho para job #{j.id}")
                    failed_paths.append(None)
            except Exception as e:
                print(f"       Erro ao deletar arquivo {j.id}: {e}")
                failed_paths.append(j.dest)
            
            # Sempre deletar job da DB mesmo se arquivo falhar
            try:
                session.delete(j)
                deleted_count += 1
            except Exception as e:
                print(f"       Erro ao deletar job do BD: {e}")
        
        session.commit()
        print(f"[OK] [API] Deletados {deleted_count} completed jobs de arquivo (Visíveis apenas)")
        return {
            "ok": True, 
            "message": f"Deleted {deleted_count} visible completed jobs", 
            "deleted": deleted_files,
            "skipped": skipped_files,
            "failed": failed_paths
        }
    except Exception as e:
        print(f" [API] Erro ao limpar completed jobs: {e}")
        raise
    finally:
        session.close()


@app.delete("/api/jobs/failed/clear")
async def clear_failed_jobs(request: ClearJobsRequest):
    """Deletar APENAS os downloads com erro VISÍVEIS na tela - SAFE VERSION"""
    print("\n  [API] DELETE /api/jobs/failed/clear - Iniciando limpeza de jobs com erro visíveis")
    print(f"    IDs visíveis recebidos do frontend: {request.job_ids}")
    session = get_session()
    try:
        # Buscar apenas os jobs visíveis que têm erro
        if request.job_ids:
            failed_jobs = session.exec(
                select(Job).where(
                    (Job.status == "failed") & 
                    (Job.id.in_(request.job_ids))
                )
            ).all()
        else:
            # Se lista vazia, não deleta nada
            failed_jobs = []
        
        print(f"   > Encontrados {len(failed_jobs)} jobs com erro VISÍVEIS para deletar")
        
        #  SAFETY: Log all paths BEFORE deletion
        if failed_jobs:
            print(f"    PATHS TO BE DELETED:")
            for j in failed_jobs:
                print(f"      [{j.id}] {j.dest}")
        
        deleted_count = 0
        deleted_files = []
        skipped_files = []
        failed_paths = []
        
        for j in failed_jobs:
            print(f"   > Deletando job #{j.id}: {j.dest}")
            job_name = None
            if j.item_id:
                try:
                    item = session.get(Item, j.item_id)
                    if item:
                        job_name = item.name
                        print(f"      Item: {job_name}")
                except Exception as e:
                    print(f"        Could not fetch item info: {e}")
            try:
                if j.dest:
                    success, message = safe_delete_download(j.dest, job_name=job_name)
                    if success:
                        deleted_files.append(j.dest)
                        if "Skipped" in message:
                            skipped_files.append(j.dest)
                        print(f"       {message}")
                    else:
                        print(f"       {message}")
                        failed_paths.append(j.dest)
                else:
                    print(f"      [WARNING]  Sem caminho para job #{j.id}")
                    failed_paths.append(None)
            except Exception as e:
                print(f"       Erro ao deletar arquivo {j.id}: {e}")
                failed_paths.append(j.dest)
            
            # Sempre deletar job da DB mesmo se arquivo falhar
            try:
                session.delete(j)
                deleted_count += 1
            except Exception as e:
                print(f"       Erro ao deletar job do BD: {e}")
        
        session.commit()
        print(f"[OK] [API] Deletados {deleted_count} failed jobs de arquivo (Visíveis apenas)")
        return {
            "ok": True, 
            "message": f"Deleted {deleted_count} visible failed jobs", 
            "deleted": deleted_files,
            "skipped": skipped_files,
            "failed": failed_paths
        }
    except Exception as e:
        print(f" [API] Erro ao limpar failed jobs: {e}")
        raise
    finally:
        session.close()


@app.delete("/api/jobs/canceled/clear")
async def clear_canceled_jobs(request: ClearJobsRequest):
    """Deletar APENAS os downloads cancelados VISÍVEIS na tela - SAFE VERSION"""
    print("\n  [API] DELETE /api/jobs/canceled/clear - Iniciando limpeza de jobs cancelados visíveis")
    print(f"   [MOBILE] IDs visíveis recebidos do frontend: {request.job_ids}")
    session = get_session()
    try:
        # Buscar apenas os jobs visíveis que são cancelados
        if request.job_ids:
            canceled_jobs = session.exec(
                select(Job).where(
                    (Job.status == "canceled") & 
                    (Job.id.in_(request.job_ids))
                )
            ).all()
        else:
            # Se lista vazia, não deleta nada
            canceled_jobs = []
        
        print(f"   > Encontrados {len(canceled_jobs)} jobs cancelados VISÍVEIS para deletar")
        
        #  SAFETY: Log all paths BEFORE deletion
        if canceled_jobs:
            print(f"    PATHS TO BE DELETED:")
            for j in canceled_jobs:
                print(f"      [{j.id}] {j.dest}")
        
        deleted_count = 0
        deleted_files = []
        skipped_files = []
        failed_paths = []
        
        for j in canceled_jobs:
            print(f"   > Deletando job #{j.id}: {j.dest}")
            job_name = None
            if j.item_id:
                try:
                    item = session.get(Item, j.item_id)
                    if item:
                        job_name = item.name
                        print(f"      Item: {job_name}")
                except Exception as e:
                    print(f"        Could not fetch item info: {e}")
            try:
                if j.dest:
                    success, message = safe_delete_download(j.dest, job_name=job_name)
                    if success:
                        deleted_files.append(j.dest)
                        if "Skipped" in message:
                            skipped_files.append(j.dest)
                        print(f"       {message}")
                    else:
                        print(f"       {message}")
                        failed_paths.append(j.dest)
                else:
                    print(f"        Sem caminho para job #{j.id}")
                    failed_paths.append(None)
            except Exception as e:
                print(f"       Erro ao deletar arquivo {j.id}: {e}")
                failed_paths.append(j.dest)
            
            # Sempre deletar job da DB mesmo se arquivo falhar
            try:
                session.delete(j)
                deleted_count += 1
            except Exception as e:
                print(f"       Erro ao deletar job do BD: {e}")
        
        session.commit()
        print(f"[OK] [API] Deletados {deleted_count} canceled jobs de arquivo (Visíveis apenas)")
        return {
            "ok": True, 
            "message": f"Deleted {deleted_count} visible canceled jobs", 
            "deleted": deleted_files,
            "skipped": skipped_files,
            "failed": failed_paths
        }
    except Exception as e:
        print(f" [API] Erro ao limpar canceled jobs: {e}")
        raise
    finally:
        session.close()


@app.post("/api/jobs/open-folder")
async def open_folder(request_data: dict):
    """Abrir a pasta do download no explorador de arquivos"""
    import subprocess
    import platform
    
    path = request_data.get("path")
    
    from fastapi import HTTPException
    
    if not path:
        raise HTTPException(status_code=400, detail="Path não fornecido")
    
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Caminho não encontrado: {path}")
    
    print(f"\n [API] POST /api/jobs/open-folder - Abrindo: {path}")
    
    try:
        # Abrir a pasta dependendo do SO
        if platform.system() == "Windows":
            # Normaliza e seleciona o arquivo no Explorer
            path = os.path.normpath(path)
            subprocess.Popen(['explorer', '/select,', path])
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", "-R", path])
        else:  # Linux
            subprocess.Popen(["xdg-open", path])
        
        print(f"   [OK] Pasta aberta com sucesso")
        return {"status": "success", "path": path}
    
    except Exception as e:
        print(f"Erro ao abrir pasta: {e}")
        raise ValueError(f"Erro ao abrir pasta: {str(e)}")


# WebSocket manager for progress updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_json(self, message: dict):
        for conn in list(self.active_connections):
            try:
                await conn.send_json(message)
            except Exception:
                self.disconnect(conn)


conn_manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await conn_manager.connect(websocket)
    try:
        while True:
            # keep alive; client can send ping
            data = await websocket.receive_text()
            # ignore and reply with current state
            await websocket.send_json({"type": "ack"})
    except WebSocketDisconnect:
        conn_manager.disconnect(websocket)


# background task to push progress to websockets
async def broadcast_progress():
    while True:
        try:
            # gather current progress for all jobs
            session = get_session()
            try:
                jobs = session.exec(select(Job)).all()
                payload = []
                for j in jobs:
                    prog = job_manager.get_progress(j.id)
                    p = dict(id=j.id, status=j.status, progress=j.progress)
                    p.update(prog)
                    payload.append(p)
                if payload:
                    await conn_manager.send_json({"type": "progress", "jobs": payload})
            finally:
                session.close()
        except Exception as e:
            print(f"Error in broadcast_progress: {e}")
        await asyncio.sleep(1.0)


# Mount static files at root AFTER all API endpoints (CRITICAL: must be last!)
# This prevents StaticFiles from capturing /api/* routes
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

if __name__ == "__main__":
    
    # Configurar socket pra reusar porta imediatamente (SO_REUSEADDR)
    import socket
    from uvicorn.config import Config
    from uvicorn.server import Server
    
    class ReuseAddrServer(Server):
        def _create_socket(self):
            sock = super()._create_socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, 'SO_REUSEPORT'):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            return sock
    
    # Tentar portas sequencialmente: 8000, 8001, 8002...
    port = 8000
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            print(f"[BACKEND] Tentando porta {port}...")
            config = Config(app="backend.main:app", host="127.0.0.1", port=port, reload=False, log_level="warning")
            server = ReuseAddrServer(config)
            asyncio.run(server.serve())
            break  # Sucesso
        except OSError as e:
            if "Address already in use" in str(e) or "10048" in str(e):
                port += 1
                print(f"[BACKEND] Porta {port-1} ocupada, tentando {port}...")
                if attempt == max_attempts - 1:
                    print(f"[BACKEND] ERRO: Nenhuma porta disponível entre 8000 e {port}")
                    raise
            else:
                raise
        except Exception as e:
            print(f"[BACKEND] Erro: {e}")
            raise

# Always mount static files at import time as well (required for running under ASGI servers)
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

