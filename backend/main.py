import sys
import os
import pathlib

# Add project root to sys.path to allow imports from 'engine'
# This is required when running from inside 'backend' folder or as a module
current_dir = pathlib.Path(__file__).parent.resolve()
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import httpx
import os
from typing import List, Optional
from datetime import datetime
import asyncio
import pathlib
import time
import zlib
import re
import unicodedata
from typing import Dict, Any, Tuple
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles
from sqlmodel import select, delete
from engine.manager import job_manager
from engine.download import supports_range
from backend.db import init_db, get_session
from backend.models.models import Source, Item, Favorite, Job, JobPart
from backend import config as backend_config
from backend.steam_service import steam_client
from backend.resolver import clear_session_cache, get_resolver_telemetry
from backend.steam_api import steam_api_client

_library_cache: Dict[str, Any] = {"valid": False, "value": None, "built_at": None, "sources_sig": None}

_magnet_health_cache: Dict[str, Any] = {}


def _magnet_cache_key(url: str) -> str:
    try:
        s = str(url or '').strip()
        if not s:
            return ''
        # Use infohash when possible (stable key), fallback to CRC32 of whole URL.
        if 'urn:btih:' in s:
            start = s.find('urn:btih:') + 9
            end = s.find('&', start)
            if end == -1:
                end = len(s)
            h = s[start:end].strip().lower()
            if h:
                return f"btih:{h}"
        return f"crc:{zlib.crc32(s.encode('utf-8')) & 0x7FFFFFFF}"
    except Exception:
        return ''


def _invalidate_library_cache() -> None:
    try:
        _library_cache["valid"] = False
    except Exception:
        pass


def _normalize_library_name(name: str) -> str:
    s = (name or "").strip()
    if not s:
        return ""
    try:
        s = unicodedata.normalize('NFKD', s)
        s = ''.join(c for c in s if not unicodedata.combining(c))
    except Exception:
        pass
    s = s.lower()
    # Drop common numeric catalog prefixes like "1428: Game Name" or "1428 - Game Name"
    s = re.sub(r"^\s*\d{1,6}\s*(?:[:\-–]+)\s*", "", s)
    s = re.sub(r"^#+", "", s)
    s = re.sub(r"\[[^\]]+\]", " ", s)
    s = re.sub(r"\([^\)]+\)", " ", s)
    s = re.sub(r"\b(v|ver|version)\s*\d+(?:\.\d+)*\b", " ", s)
    s = re.sub(r"\b(build|b)\s*\d+(?:\.\d+)*\b", " ", s)
    s = re.sub(r"\b(update|patch|hotfix)\s*\d+(?:\.\d+)*\b", " ", s)
    s = re.sub(r"\b\d+(?:\.\d+){1,}\b", " ", s)
    s = re.sub(r"\b(release|final|proper|complete|deluxe|ultimate|remaster(?:ed)?|definitive|bundle|redux)\b", " ", s)
    s = re.sub(r"\b(multi\s*\d+|multi\d+)\b", " ", s)
    s = re.sub(r"\bupdate\s+from\b.*", " ", s) # Clean "Update From v1 to v2" entirely
    s = re.sub(r"\b(selective\s*download|repack)\b", " ", s)
    s = re.sub(r"\b(repack|fitgirl|dodi|elamigos|gog|steamrip|codex|plaza|skidrow|reloaded|goldberg|tenoke|xatab)\b", " ", s)
    # Platform/compatibility noise often appended to titles
    s = re.sub(r"\bwindows\s*(?:xp|vista|7|8|8\.1|10|11)(?:\s*-\s*(?:xp|vista|7|8|8\.1|10|11))*\b", " ", s)
    s = re.sub(r"\bwin\s*(?:xp|7|8|8\.1|10|11)\b", " ", s)
    s = re.sub(r"\b(?:compatible|compatibility)\b", " ", s)
    s = re.sub(r"\s*(?:\+|\-|–|:|\|)\s*[^\n]*\b(dlc|dlcs|ost|soundtrack|bonus|pack|collection|edition|bundle)\b[^\n]*", " ", s)
    # Mod-related descriptors at the end shouldn't split the same base game into separate groups
    # (kept conservative to avoid breaking titles like "garry's mod" which won't match as a suffix segment)
    s = re.sub(r"\s*(?:\+|\-|–|:|\|)\s*[^\n]*\b(modpack|mod\s*pack|mods|mod|retexture(?:d)?|retextured|texture(?:d)?|graphics|redux|overhaul|remastered\s*mod)\b[^\n]*", " ", s)

    # Specific normalization: GTA variants should be grouped together
    # This handles Legacy/Enhanced/Definitive/Nextgen editions
    try:
        # GTA V specific
        if re.search(r"\b(grand\s+theft\s+auto\s+v|gta\s*5|gta\s*v)\b", s):
            s = re.sub(r"\bgta\s*5\b", "grand theft auto v", s)
            s = re.sub(r"\bgta\s*v\b", "grand theft auto v", s)
            s = re.sub(r"\b(legacy|enhanced|online)\b", " ", s)
            s = re.sub(r"\bpremium\b", " ", s)
            s = re.sub(r"grand theft auto v[\W_]+grand theft auto v", "grand theft auto v", s)
        
        # GTA IV specific
        elif re.search(r"\b(grand\s+theft\s+auto\s+iv|gta\s*4|gta\s*iv)\b", s):
            s = re.sub(r"\bgta\s*4\b", "grand theft auto iv", s)
            s = re.sub(r"\bgta\s*iv\b", "grand theft auto iv", s)
        
        # GTA San Andreas specific
        elif re.search(r"\b(grand\s+theft\s+auto.*san\s+andreas|gta.*san\s+andreas)\b", s):
            s = re.sub(r"\bgta\b", "grand theft auto", s)
            s = re.sub(r"\bnextgen\b", " ", s)
            s = re.sub(r"\b(definitive|remastered|edition)\b", " ", s)
        
        # GTA Vice City specific  
        elif re.search(r"\b(grand\s+theft\s+auto.*vice\s+city|gta.*vice\s+city)\b", s):
            s = re.sub(r"\bgta\b", "grand theft auto", s)
            s = re.sub(r"\bnextgen\b", " ", s)
            s = re.sub(r"\b(definitive|remastered|edition)\b", " ", s)
        
        # GTA III specific
        elif re.search(r"\b(grand\s+theft\s+auto\s+iii|gta\s*3|gta\s*iii)\b", s):
            s = re.sub(r"\bgta\s*3\b", "grand theft auto iii", s)
            s = re.sub(r"\bgta\s*iii\b", "grand theft auto iii", s)
            s = re.sub(r"\b(anniversary|hd|edition)\b", " ", s)
    except Exception:
        pass

    s = re.sub(r"\b\d{6,}\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _library_group_key(item: Dict[str, Any]) -> str:
    for k in ("appId", "appid", "steam_appid", "steamAppId", "steam_app_id"):
        v = item.get(k)
        try:
            if v is None:
                continue
            sv = str(v).strip()
            if not sv:
                continue
            if sv.isdigit():
                return f"steam:{int(sv)}"
        except Exception:
            pass
    base = _normalize_library_name(str(item.get('name') or ''))
    if base:
        return base
    url = str(item.get('url') or '')
    url = url.strip().lower()
    if not url:
        return "unknown"
    # stable-ish fallback to avoid empty grouping
    return f"url:{zlib.crc32(url.encode('utf-8')) & 0x7FFFFFFF}"


def _extract_library_app_id(item: Dict[str, Any]) -> Optional[int]:
    for k in ("appId", "appid", "steam_appid", "steamAppId", "steam_app_id"):
        try:
            v = item.get(k)
            if v is None:
                continue
            sv = str(v).strip()
            if not sv or not sv.isdigit():
                continue
            return int(sv)
        except Exception:
            continue
    return None


def _coerce_int(v: Any) -> Optional[int]:
    try:
        if v is None:
            return None
        if isinstance(v, bool):
            return int(v)
        return int(v)
    except Exception:
        return None


def _upload_date_to_ts(v: Any) -> int:
    if v is None:
        return 0
    try:
        if isinstance(v, (int, float)):
            iv = int(v)
            if iv > 10_000_000_000:
                iv = iv // 1000
            return iv
    except Exception:
        pass

    s = str(v).strip()
    if not s:
        return 0

    try:
        dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except Exception:
        pass

    try:
        if s.isdigit():
            iv = int(s)
            if iv > 10_000_000_000:
                iv = iv // 1000
            return iv
    except Exception:
        pass

    try:
        m = re.search(r"(\d+)\s*(second|minute|hour|day|week|month|year)s?", s.lower())
        if m:
            n = int(m.group(1))
            unit = m.group(2)
            mult = {
                "second": 1,
                "minute": 60,
                "hour": 3600,
                "day": 86400,
                "week": 7 * 86400,
                "month": 30 * 86400,
                "year": 365 * 86400,
            }.get(unit, 0)
            if mult > 0:
                return int(datetime.utcnow().timestamp()) - (n * mult)
    except Exception:
        pass

    return 0


def _pick_best_version(versions: List[Dict[str, Any]]) -> Dict[str, Any]:
    def score(x: Dict[str, Any]) -> Tuple[int, int, int, int]:
        ts = _upload_date_to_ts(x.get('uploadDate'))
        seeders = _coerce_int(x.get('seeders')) or 0
        leechers = _coerce_int(x.get('leechers')) or 0
        size = _coerce_int(x.get('size')) or 0
        # Primary: most recent. Secondary: health/seeders. Tertiary: size.
        return (ts, seeders, leechers, size)

    best = None
    best_score = None
    for v in versions:
        sc = score(v)
        if best is None or sc > best_score:
            best = v
            best_score = sc
    return best or (versions[0] if versions else {})


async def _build_library_payload() -> Dict[str, Any]:
    session = get_session()
    try:
        sources = session.exec(select(Source)).all()
        sources_sig = '|'.join([f"{s.id}:{s.url}:{s.title}:{getattr(s, 'created_at', '')}" for s in sources])
    finally:
        session.close()

    groups: Dict[str, Dict[str, Any]] = {}
    total_items = 0

    for s in sources:
        if not s.url and not getattr(s, 'data', None):
            continue
        try:
            source_items = await _load_items_internal(s)
        except Exception:
            source_items = []
        total_items += len(source_items)
        source_title = s.title or (s.url or f"Source #{s.id}")
        for it in source_items:
            if not isinstance(it, dict):
                continue
            it = dict(it)
            it.setdefault('source_id', s.id)
            it.setdefault('source_title', source_title)
            key = _library_group_key(it)
            g = groups.get(key)
            if not g:
                groups[key] = {"key": key, "display_name": it.get('name') or key, "versions": [it]}
            else:
                g["versions"].append(it)

    #  MERGE PASS: Unify "Name Only" groups into "Steam ID" groups
    # This fixes split cards where some items have AppID and others don't (e.g. GTA V)
    
    # 1. Map Normalized Name -> Steam Group Key
    name_to_steam_key = {}
    for key, g in groups.items():
        if key.startswith("steam:"):
            # Find the most frequent name or just usage the first valid one
            # Use _normalize_library_name on the group's versions
            candidates = {}
            for v in g["versions"]:
                n = _normalize_library_name(str(v.get("name") or ""))
                if n:
                    candidates[n] = candidates.get(n, 0) + 1
            
            if candidates:
                # Pick most common name
                best_name = max(candidates.items(), key=lambda x: x[1])[0]
                name_to_steam_key[best_name] = key


    # 2. Merge Name Groups into Steam Groups
    keys_to_remove = []
    for key, g in groups.items():
        if not key.startswith("steam:") and not key.startswith("url:"):
            # This is likely a Name group (key is the normalized name)
            target_steam_key = name_to_steam_key.get(key)
            if target_steam_key and target_steam_key in groups:
                 # MERGE!
                 target_group = groups[target_steam_key]
                 target_group["versions"].extend(g["versions"])
                 keys_to_remove.append(key)
    
    for k in keys_to_remove:
        del groups[k]
    
    # DEBUG: Show all groups before second merge
    print(f"\n[DEBUG] Grupos antes do segundo merge: {len(groups)}")
    gta_groups = {k: g for k, g in groups.items() if 'grand theft auto' in g.get('display_name', '').lower()}
    if gta_groups:
        print("[DEBUG] Grupos GTA encontrados:")
        for key, g in gta_groups.items():
            print(f"  - {key}: '{g.get('display_name')}' ({len(g.get('versions', []))} versões)")
    
    # 3. SECOND MERGE PASS: Consolidate Steam groups with identical normalized names
    # This handles cases like GTA San Andreas (AppID 12120) + GTA San Andreas Definitive (AppID 1547000)
    # Both normalize to "grand theft auto san andreas" but have different AppIDs
    
    # Build reverse map: normalized_name -> list of steam keys
    normalized_to_steam_keys: Dict[str, List[str]] = {}
    for key, g in groups.items():
        if key.startswith("steam:"):
            candidates = {}
            for v in g["versions"]:
                n = _normalize_library_name(str(v.get("name") or ""))
                if n:
                    candidates[n] = candidates.get(n, 0) + 1
            
            if candidates:
                best_name = max(candidates.items(), key=lambda x: x[1])[0]
                if best_name not in normalized_to_steam_keys:
                    normalized_to_steam_keys[best_name] = []
                normalized_to_steam_keys[best_name].append(key)
    
    # Merge duplicates: keep the first, merge others into it
    keys_to_remove_2 = []
    for norm_name, steam_keys in normalized_to_steam_keys.items():
        if len(steam_keys) > 1:
            print(f"[MERGE] Consolidando '{norm_name}': {len(steam_keys)} grupos Steam -> 1 grupo")
            # Keep first, merge rest
            primary_key = steam_keys[0]
            primary_group = groups[primary_key]
            
            for secondary_key in steam_keys[1:]:
                secondary_group = groups[secondary_key]
                print(f"  - Mesclando {secondary_key} ({len(secondary_group['versions'])} versões) em {primary_key}")
                primary_group["versions"].extend(secondary_group["versions"])
                keys_to_remove_2.append(secondary_key)
    
    for k in keys_to_remove_2:
        del groups[k]
    
    if keys_to_remove_2:
        print(f"[MERGE] Total de grupos mesclados: {len(keys_to_remove_2)}")

    out_groups: List[Dict[str, Any]] = []
    for key, g in groups.items():
        versions = g.get('versions') or []

        # Propagate Steam AppID inside the group if any version has it.
        # This is intentionally conservative (does not merge groups) and helps
        # image caching/resolution on the frontend.
        group_app_id: Optional[int] = None
        try:
            for v in versions:
                aid = _extract_library_app_id(v)
                if aid:
                    group_app_id = aid
                    break
        except Exception:
            group_app_id = None

        if group_app_id:
            for v in versions:
                try:
                    if _extract_library_app_id(v) is None:
                        v["appId"] = group_app_id
                        v["steam_appid"] = group_app_id
                except Exception:
                    pass

        best = _pick_best_version(versions)
        if group_app_id:
            try:
                if _extract_library_app_id(best) is None:
                    best["appId"] = group_app_id
                    best["steam_appid"] = group_app_id
            except Exception:
                pass
        recent_ts = 0
        try:
            recent_ts = max((_upload_date_to_ts(x.get('uploadDate')) for x in versions), default=0)
        except Exception:
            recent_ts = _upload_date_to_ts(best.get('uploadDate'))
        display_name = best.get('name') or g.get('display_name') or key
        merged = {
            "key": key,
            "name": display_name,
            "appId": group_app_id,
            "steam_appid": group_app_id,
            "versions_count": len(versions),
            "best": best,
            "versions": sorted(
                versions,
                key=lambda x: (
                    _upload_date_to_ts(x.get('uploadDate')),
                    _coerce_int(x.get('seeders')) or 0,
                    _coerce_int(x.get('leechers')) or 0,
                    _coerce_int(x.get('size')) or 0,
                    str(x.get('uploadDate') or '')
                ),
                reverse=True
            ),
            "recent_ts": recent_ts,
        }
        out_groups.append(merged)

    out_groups.sort(key=lambda x: (-_coerce_int(x.get('recent_ts')) or 0, str(x.get('name') or '').lower()))
    return {
        "groups": out_groups,
        "total_sources": len(sources),
        "total_items": total_items,
        "built_at": datetime.utcnow().isoformat() + 'Z',
        "sources_sig": sources_sig,
    }


async def library_index(refresh: bool = False):
    if not refresh and _library_cache.get("valid") and _library_cache.get("value") is not None:
        return _library_cache["value"]

    payload = await _build_library_payload()
    try:
        _library_cache["valid"] = True
        _library_cache["value"] = payload
        _library_cache["built_at"] = payload.get("built_at")
        _library_cache["sources_sig"] = payload.get("sources_sig")
    except Exception:
        pass
    return payload

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
        print(f" Found {len(running_jobs)} jobs that were running before restart")
        print(f"   Auto-pausing to prevent state confusion...")
        for j in running_jobs:
            j.status = "paused"
            session.add(j)
        session.commit()
        print(f" {len(running_jobs)} jobs marked as paused")
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
app.get("/api/library")(library_index)


@app.get("/api/system/default-path")
def get_system_default_path():
    """
    Retorna o caminho padrão de Downloads do sistema.
    Útil como fallback se o Electron IPC falhar.
    """
    try:
        home = pathlib.Path.home()
        downloads = home / "Downloads"
        if not downloads.exists():
            downloads = home  # Fallback to home if no Downloads folder
        return {"path": str(downloads.absolute())}
    except Exception as e:
        return {"path": "", "error": str(e)}



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
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": "https://store.steampowered.com/",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, follow_redirects=True, headers=headers)
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

        _invalidate_library_cache()
        
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

        _invalidate_library_cache()

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
    #  CRITICAL FIX: Ignore relative paths (like "downloads") to prevent writing to app dir
    raw_dest = req.destination or req.dest
    download_dest = None
    
    if raw_dest:
        if os.path.isabs(raw_dest):
            download_dest = raw_dest
        else:
            print(f" [WARN] Relative path ignored: {raw_dest}")
            
    if not download_dest:
        download_dest = backend_config.DOWNLOADS_DIR
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
        items.append(dict(id=j.id, item_id=j.item_id, status=j.status, progress=j.progress or prog.get('progress'), created_at=j.created_at.isoformat(), updated_at=j.updated_at.isoformat(), last_error=j.last_error, item_name=(item.name if item else None), item_url=(item.url if item else None), dest=j.dest, downloaded=prog.get('downloaded'), total=prog.get('total') or j.size, speed=prog.get('speed'), size=j.size))
    session.close()
    return items


@app.get("/api/sources")
async def list_sources():
    session = get_session()
    q = session.exec(select(Source)).all()
    result = [dict(id=s.id, url=s.url, title=s.title, created_at=s.created_at.isoformat()) for s in q]
    session.close()
    return result


class FavoriteCreateReq(BaseModel):
    source_id: int
    item_id: int
    name: str
    url: str
    image: Optional[str] = None


def stable_item_id(url: str) -> int:
    u = (url or "").strip()
    if not u:
        return 0
    return zlib.crc32(u.encode("utf-8")) & 0x7FFFFFFF


@app.get("/api/favorites")
async def list_favorites():
    session = get_session()
    q = session.exec(select(Favorite).order_by(Favorite.created_at.desc())).all()

    changed = False
    for f in q:
        new_item_id = stable_item_id(f.url)
        if new_item_id and f.item_id != new_item_id:
            dup = session.exec(
                select(Favorite).where(
                    (Favorite.source_id == f.source_id)
                    & (Favorite.item_id == new_item_id)
                    & (Favorite.id != f.id)
                )
            ).first()

            if dup:
                # Keep the newest favorite record
                if dup.created_at >= f.created_at:
                    session.delete(f)
                else:
                    session.delete(dup)
                    f.item_id = new_item_id
                    session.add(f)
            else:
                f.item_id = new_item_id
                session.add(f)

            changed = True

    if changed:
        session.commit()
        q = session.exec(select(Favorite).order_by(Favorite.created_at.desc())).all()

    out = [
        dict(
            id=f.id,
            source_id=f.source_id,
            item_id=f.item_id,
            name=f.name,
            url=f.url,
            image=f.image,
            created_at=f.created_at.isoformat() if f.created_at else None,
        )
        for f in q
    ]
    session.close()
    return out


@app.post("/api/favorites")
async def create_favorite(req: FavoriteCreateReq):
    session = get_session()

    req_item_id = req.item_id
    computed_item_id = stable_item_id(req.url)
    if computed_item_id:
        req_item_id = computed_item_id

    existing = session.exec(
        select(Favorite).where(
            (Favorite.source_id == req.source_id) & (Favorite.item_id == req_item_id)
        )
    ).first()

    if existing:
        existing.name = req.name
        existing.url = req.url
        if req.image:
            existing.image = req.image
        session.add(existing)
        session.commit()
        session.refresh(existing)
        out = dict(
            id=existing.id,
            source_id=existing.source_id,
            item_id=existing.item_id,
            name=existing.name,
            url=existing.url,
            image=existing.image,
            created_at=existing.created_at.isoformat() if existing.created_at else None,
        )
        session.close()
        return out

    fav = Favorite(source_id=req.source_id, item_id=req_item_id, name=req.name, url=req.url, image=req.image)
    session.add(fav)
    session.commit()
    session.refresh(fav)

    out = dict(
        id=fav.id,
        source_id=fav.source_id,
        item_id=fav.item_id,
        name=fav.name,
        url=fav.url,
        image=fav.image,
        created_at=fav.created_at.isoformat() if fav.created_at else None,
    )
    session.close()
    return out


@app.delete("/api/favorites/by_item")
async def delete_favorite_by_item(source_id: int, item_id: int):
    session = get_session()
    session.exec(
        delete(Favorite).where(
            (Favorite.source_id == source_id) & (Favorite.item_id == item_id)
        )
    )
    session.commit()
    session.close()
    return {"status": "deleted", "source_id": source_id, "item_id": item_id}




def stable_item_id(url_or_magnet: str) -> int:
    import zlib
    if not url_or_magnet:
        return 0
    return zlib.crc32(str(url_or_magnet).encode('utf-8'))

async def _load_items_internal(source: Source):
    """Internal helper to fetch and parse items from a source object."""
    print(f"[OK] Fonte encontrada: {source.url or 'JSON colado'}")    
    
    js = None
    # Se for URL, fazer releitura do JSON
    if source.url and not source.url.startswith("json-raw://"):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(source.url, follow_redirects=True, timeout=20.0)
                if r.status_code >= 400:
                    print(f" Erro status code: {r.status_code}")
                    return []
                js = r.json()
                print(f"[OK] JSON recarregado - {len(str(js))} bytes")
        except Exception as e:
            print(f" Erro ao recarregar fonte: {str(e)}")
            # Don't raise HTTP exception here, just return empty list to allow iteration to continue
            return []
    elif source.data:
        # Se for JSON colado, recuperar do campo data
        import json
        try:
            js = json.loads(source.data)
            print(f"[OK] JSON colado recuperado - {len(source.data)} bytes")
        except Exception as e:
            print(f" Erro ao parsear JSON colado: {str(e)}")
            return []
    else:
        # Se for JSON colado mas sem dados, não temos forma de recuperar - retornar vazio
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
        
        # Extrair Seeds/Peers para análise de saúde
        seeders = raw.get("seeders") or raw.get("seeds")
        leechers = raw.get("leechers") or raw.get("peers")
        
        items.append(dict(
            id=stable_item_id(u),
            name=name or str(u).split("/")[-1],
            url=u,
            size=size,
            category=cat,
            type=item_type,
            source_id=source.id,
            image=image,
            icon=icon,
            thumbnail=thumbnail,
            uploadDate=upload_date,
            seeders=seeders,
            leechers=leechers
        ))
    
    return items

@app.get("/api/sources/{source_id}/items")
async def list_items(source_id: int):
    """Carrega items sob demanda da fonte (releitura do JSON)."""
    print(f"\n[INFO] GET /api/sources/{source_id}/items - Carregando items sob demanda")
    
    session = get_session()
    source = session.get(Source, source_id)
    if not source:
        session.close()
        raise HTTPException(status_code=404, detail="Source not found")
        
    items = await _load_items_internal(source)
    
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

    _invalidate_library_cache()
    
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


@app.get("/api/resolver/telemetry")
async def resolver_telemetry():
    return get_resolver_telemetry()


@app.post("/api/resolver/telemetry/reset")
async def resolver_telemetry_reset():
    try:
        before = get_resolver_telemetry()
        from backend import resolver as _resolver_mod
        if hasattr(_resolver_mod, "_resolver_telemetry") and isinstance(_resolver_mod._resolver_telemetry, dict):
            for k in list(_resolver_mod._resolver_telemetry.keys()):
                _resolver_mod._resolver_telemetry[k] = 0
        return {"status": "ok", "before": before, "after": get_resolver_telemetry()}
    except Exception:
        return {"status": "ok"}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int):
    session = get_session()
    try:
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
        # merge progress data
        out.update(prog)
        return out
    finally:
        session.close()


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
    return {"ok": True, "message": "Job canceled and cleaned up"}


@app.get("/api/sources/{source_id}/items/{item_id}")
async def get_source_item(source_id: int, item_id: int):
    """Fetches a single item from a source by its ID (hash)."""
    # Reuse the logic from list_items - simpler to just call list_items logic internally
    items = await list_items(source_id)
    for item in items:
        if item.get('id') == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found in source")


class AnalyzeReq(BaseModel):
    item: dict

async def _analysis_core(req: AnalyzeReq):
    """Core analysis logic shared by both endpoints."""
    try:
        from backend.services.analysis import ItemMatchingService, SourceHealthService
    except ImportError:
        # Fallback for when running directly or path issues
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from backend.services.analysis import ItemMatchingService, SourceHealthService

    print(f"\n[ANALYSIS] Iniciando análise para: {req.item.get('name')}")
    
    session = get_session()
    sources = session.exec(select(Source)).all()
    
    from types import SimpleNamespace
    candidates = []
    # Use SimpleNamespace instead of Item model to allow dynamic attribute injection (seeders/leechers)
    target_item_obj = SimpleNamespace(**req.item) if isinstance(req.item, dict) else req.item
    # Ensure name is set for matching
    if not target_item_obj.name:
         target_item_obj.name = req.item.get('name', 'Unknown')

    # 1. Fetch items from all sources and collect matches
    all_raw_matches = []
    
    for source in sources:
        # Skip if source has no URL (unless it has data)
        if not source.url and not source.data:
            continue
            
        # Helper returns list of dicts
        source_items = await _load_items_internal(source)
        
        # Convert dicts to pseudo-items for matching
        from types import SimpleNamespace
        source_objs = []
        for i in source_items:
            obj = SimpleNamespace(**i)
            # Add metadata needed later
            obj.source_title = source.title
            obj.source_id = source.id
            source_objs.append(obj)
            
        # Find equivalents in this source
        matches = ItemMatchingService.find_equivalents(target_item_obj, source_objs + [])
        
        for m in matches:
            # Don't suggest the exact same item from same source
            if str(m.id) == str(target_item_obj.id) and str(m.source_id) == str(target_item_obj.source_id):
                continue
            all_raw_matches.append(m)

    print(f"[ANALYSIS] Initial matches found: {len(all_raw_matches)}. Starting live probe...")
    
    # 2. PROBE LIVE HEALTH (UDP Scraper)
    target_item_obj.url = req.item.get('url')
    items_to_probe = all_raw_matches + [target_item_obj]
    
    if items_to_probe:
        await SourceHealthService.enrich_candidates(items_to_probe)

    # 3. Build final response
    original_health = SourceHealthService.calculate_health_score(target_item_obj.__dict__)
    
    for m in all_raw_matches:
        d = m.__dict__
        health = SourceHealthService.calculate_health_score(d)
        
        candidates.append({
            "item": d,
            "source_title": getattr(m, 'source_title', 'Unknown'),
            "health": health,
            "is_original": False
        })

    session.close()
    
    # Sort by Health Score
    candidates.sort(key=lambda x: (x['health']['score'], x['health']['seeders'] or 0), reverse=True)
    
    print(f"[ANALYSIS] Encontradas {len(candidates)} alternativas.")
    return {
        "candidates": candidates,
        "original_health": original_health
    }

@app.post("/api/analysis/pre-job")
async def pre_job_analysis(req: AnalyzeReq):
    """
    Analyzes all available sources to find healthier alternatives for the target item.
    """
    return await _analysis_core(req)


@app.post("/api/analysis/pre-job/with-recommendations")
async def pre_job_analysis_with_recommendations(req: AnalyzeReq):
    """
    Analyzes all available sources to find healthier alternatives for the target item.
    Alias endpoint for frontend compatibility.
    """
    return await _analysis_core(req)


class MagnetHealthReq(BaseModel):
    url: str
    force_refresh: Optional[bool] = False


@app.post("/api/magnet/health")
async def magnet_health(req: MagnetHealthReq):
    """Probe magnet health (seeders/leechers) locally using UDP trackers.

    This endpoint is optimized for pre-flight checks:
    - Small payload
    - In-memory TTL cache to avoid tracker spam
    - Short timeout
    """
    url = (req.url or '').strip()
    if not url or not url.startswith('magnet:'):
        raise HTTPException(status_code=400, detail="url must be a magnet link")

    ttl_sec = int(os.environ.get('MAGNET_HEALTH_CACHE_TTL_SEC', '600') or 600)
    timeout_sec = float(os.environ.get('MAGNET_HEALTH_TIMEOUT_SEC', '4.0') or 4.0)
    if req.force_refresh:
        timeout_sec = float(os.environ.get('MAGNET_HEALTH_FORCE_TIMEOUT_SEC', '20.0') or 20.0)
    cache_key = _magnet_cache_key(url)

    now = time.time()
    print(f"[MAGNET-HEALTH] Cache key: {cache_key}, force_refresh: {req.force_refresh}")
    stale_cache_fallback = None
    stale_cache_age_sec = None
    if cache_key and not req.force_refresh:
        try:
            cached = _magnet_health_cache.get(cache_key)
            if cached and isinstance(cached, dict):
                ts = float(cached.get('ts') or 0)
                if ts > 0 and (now - ts) <= ttl_sec:
                    print(f"[MAGNET-HEALTH] Usando cache com {int(now - ts)}s de idade")
                    out = dict(cached.get('data') or {})
                    out.update({"cached": True, "cache_age_sec": int(now - ts), "took_ms": 0})
                    return out
        except Exception:
            pass
    elif cache_key and req.force_refresh:
        # Keep any existing cache as a fallback if the live probe times out.
        try:
            cached = _magnet_health_cache.get(cache_key)
            if cached and isinstance(cached, dict):
                ts = float(cached.get('ts') or 0)
                if ts > 0:
                    stale_cache_fallback = dict(cached.get('data') or {})
                    stale_cache_age_sec = int(now - ts)
        except Exception:
            stale_cache_fallback = None
            stale_cache_age_sec = None

    t0 = time.time()
    try:
        from backend.services.analysis import SourceHealthService
        from backend.utils.tracker import UDPTrackerClient
    except ImportError:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from backend.services.analysis import SourceHealthService
        from backend.utils.tracker import UDPTrackerClient

    # Probe a single-item list in-place, with extra trackers for better consistency with pre-job.
    TRACKERS_EXTRAS = [
        "udp://tracker.opentrackr.org:1337/announce",
        "udp://open.stealth.si:80/announce",
        "udp://tracker.torrent.eu.org:451/announce",
        "udp://exodus.desync.com:6969/announce",
        "udp://tracker.moeking.me:6969/announce",
        "udp://tracker.openbittorrent.com:6969/announce",
        "udp://opentracker.i2p.rocks:6969/announce",
        "udp://tracker.internetwarriors.net:1337/announce",
        "udp://explodie.org:6969/announce",
        "udp://tracker.cyberia.is:6969/announce",
        "udp://tracker.birkenwald.de:6969/announce",
        "udp://tracker.tiny-vps.com:6969/announce",
        "udp://retracker.lanta-net.ru:2710/announce",
        "udp://ipv4.tracker.harry.lu:80/announce",
        "udp://tracker.theoks.net:6969/announce",
        "udp://tracker.ccp.ovh:6969/announce",
        "udp://bt1.archive.org:6969/announce",
        "udp://bt2.archive.org:6969/announce",
        "udp://tracker.filemail.com:6969/announce",
        "udp://tracker1.bt.moack.co.kr:80/announce",
        "udp://9.rarbg.com:2810/announce",
        "udp://tracker.uw0.xyz:6969/announce",
    ]
    # Append extra trackers to maximize chances of finding seeds (same as SourceHealthService)
    full_url = url
    for tr in TRACKERS_EXTRAS:
        full_url += f"&tr={tr}"
    item_dict: Dict[str, Any] = {"url": full_url, "seeders": 0, "leechers": 0}

    # CRITICAL FIX: Always use partial probe for preflight checks (fast, returns partial results)
    # Prejob analysis uses SourceHealthService.enrich_candidates() separately (slower, full results)
    timed_out = False
    responded = None
    total = None
    
    # Use partial probe for both force_refresh and normal mode
    # This ensures we get results even if some trackers are slow
    try:
        mode_label = "force_refresh=True" if req.force_refresh else "normal"
        print(f"[MAGNET-HEALTH] Iniciando sondagem {mode_label} (partial) timeout={timeout_sec}s")
        client_timeout = float(os.environ.get('MAGNET_TRACKER_TIMEOUT_SEC', '2.0') or 2.0)
        client_retries = int(os.environ.get('MAGNET_TRACKER_RETRIES', '2') or 2)
        client = UDPTrackerClient(timeout=client_timeout, retries=client_retries)
        stats = await client.get_stats_partial(full_url, overall_timeout=timeout_sec)
        if stats and isinstance(stats, dict):
            responded = int(stats.get('responded') or 0)
            total = int(stats.get('total') or 0)
            timed_out = bool(stats.get('timed_out'))
            item_dict['seeders'] = int(stats.get('seeders') or 0)
            item_dict['leechers'] = int(stats.get('leechers') or 0)
        print(f"[MAGNET-HEALTH] Sondagem parcial concluída. Seeds={item_dict.get('seeders')} Leechers={item_dict.get('leechers')} responded={responded}/{total} timed_out={timed_out}")
    except Exception as e:
        timed_out = True
        print(f"[MAGNET-HEALTH] Erro na sondagem parcial: {e}")

    health = SourceHealthService.calculate_health_score(item_dict)
    took_ms = int((time.time() - t0) * 1000)
    out = {
        "seeders": health.get('seeders'),
        "leechers": health.get('leechers'),
        "score": health.get('score'),
        "label": health.get('label'),
        "color": health.get('color'),
        "cached": False,
        "timed_out": timed_out,
        "responded": responded,
        "total": total,
        "took_ms": took_ms,
    }

    # If the live probe timed out, prefer returning the last good cached value instead of 0/0.
    # For force_refresh, ONLY fallback if no tracker replied (responded=0) to keep the result as live as possible.
    if timed_out and stale_cache_fallback and isinstance(stale_cache_fallback, dict) and (not req.force_refresh or int(responded or 0) == 0):
        try:
            fallback_out = dict(stale_cache_fallback)
            fallback_out.update({
                "cached": True,
                "cache_age_sec": stale_cache_age_sec,
                "timed_out": True,
                "used_stale_cache": True,
                "responded": responded,
                "total": total,
                "took_ms": took_ms,
            })
            print(f"[MAGNET-HEALTH] Timeout -> usando fallback do cache: age={stale_cache_age_sec}s seeders={fallback_out.get('seeders')} leechers={fallback_out.get('leechers')}")
            return fallback_out
        except Exception:
            pass

    # Não cachear quando houve timeout, pois pode retornar 0/0 mesmo com trackers respondendo.
    if cache_key and not timed_out:
        try:
            _magnet_health_cache[cache_key] = {"ts": now, "data": out}
        except Exception:
            pass

    print(f"[MAGNET-HEALTH] Retornando: cached=False, took_ms={took_ms}, seeders={out.get('seeders')}, leechers={out.get('leechers')}")
    return out



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
                    prog = job_manager.get_progress(j.id) or {}
                    p = dict(
                        id=j.id, 
                        status=j.status, 
                        progress=j.progress, 
                        size=j.size,  # Ensure size is sent (critical for completed jobs)
                        total=prog.get('total') or j.size, # Fallback to size if total is missing
                        downloaded=prog.get('downloaded'),
                        speed=prog.get('speed')
                    )
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

# Ensure frontend_path is defined
frontend_path = pathlib.Path(__file__).parent.parent / "frontend" / "dist"

if frontend_path.exists():
    @app.get("/")
    async def serve_index():
        return FileResponse(frontend_path / "index.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

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

