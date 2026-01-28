import httpx
import asyncio
import time
import json
import os
import re
import difflib
import zlib
from datetime import datetime
from typing import Dict, Optional, Any, List, Set, Tuple

# --- FERRAMENTAS CRÍTICAS DE PERSISTÊNCIA (ACESSO GLOBAL) ---
from backend.db import get_session, get_db_file_path, init_db
from backend.models.models import GameMetadata, SteamApp
from sqlmodel import select
from sqlalchemy import func

print(">>> [TRACE] STEAM_SERVICE.PY VERSION 3.6: PERSISTENCE HARDENED <<<")

_env_app_list_file = os.environ.get("STEAM_APP_LIST_FILE")
_env_app_data_dir = os.environ.get("APP_DATA_DIR")
if _env_app_list_file:
    APP_LIST_FILE = _env_app_list_file
elif _env_app_data_dir:
    os.makedirs(_env_app_data_dir, exist_ok=True)
    APP_LIST_FILE = os.path.join(_env_app_data_dir, "steam_applist.json")
else:
    _local_app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if _local_app_data:
        _default_dir = os.path.join(_local_app_data, "furiousapp")
        os.makedirs(_default_dir, exist_ok=True)
        APP_LIST_FILE = os.path.join(_default_dir, "steam_applist.json")
    else:
        APP_LIST_FILE = "steam_applist.json"

APP_LIST_URL_OFFICIAL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
APP_LIST_URL_FALLBACK = "https://raw.githubusercontent.com/dgibbs64/SteamCMD-AppID-List/main/steamcmd_appid.json"

from backend.config import STEAMGRIDDB_API_KEY
from backend.image_service import SteamGridDBProvider
from backend.steam_api import steam_api_client

class SteamClient:
    def normalize_game_name(self, name: str) -> str:
        if not name: return ""
        s = str(name).strip()
        replacements = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."}
        for k, v in replacements.items(): s = s.replace(k, v)
        from urllib.parse import unquote
        s = unquote(s)
        
        # 1. Basic Cleaning
        s = re.sub(r'[\(\[].*?[\)\]]', '', s)
        s = re.sub(r'http\S+', '', s)
        
        # 2. Keywords (Editions, Types)
        keywords = r'(?i)\b(release|final|proper|complete|deluxe|ultimate|remaster(?:ed)?|definitive|bundle|redux|legendary|anniversary|goty|game of the year|director\'s cut|collectors|premium|gold|platinum|standard|special|limited|enchanced|edition|pack|collection|anthology|trilogy|quadrilogy|saga|series|franchise)\b'
        s = re.sub(keywords, ' ', s)
        
        # 3. Scene Tags & Garbage
        # specific handling for "build", "update" followed by numbers (with or without spaces) or dots
        s = re.sub(r'(?i)\b(build|update|patch|revision|season|year)\s*\d+(?:[\s\.]\d+)*', ' ', s)
        
        scene_tags = r'(?i)\b(repack|dodi|fitgirl|elamigos|empress|cpy|codex|skidrow|reloaded|plaza|hi2u|kaos|prophet|razor1911|flt|tenoke|rune|goldberg|online|multi(?:layer)?|multi\d+|dlc|dlcs|crack(?:ed)?|fix|bonus(?:es)?|emulator|switch)\b'
        s = re.sub(scene_tags, ' ', s)

        # 4. Versions: "v1.0", "v 1 0", "1.0.1"
        # Handles "v" followed by digit groups separated by dot or space
        s = re.sub(r'(?i)\bv\s*\d+(?:[\.\s]\d+)+[a-z]?\b', ' ', s)
        
        # 5. Remove "loose" numeric versions at the END of the string
        # e.g. "F1 2016 1 8 0" -> "1 8 0" is 3 numeric groups.
        s = re.sub(r'(?:\s+\d+){3,}$', ' ', s)

        # 6. Cleanup
        s = re.sub(r'[^a-zA-Z0-9\s\']', ' ', s) # Allow apostrophes for names like "Assassin's"
        words = s.split()
        
        return " ".join(words).lower()

    def get_synthetic_id(self, name: str) -> int:
        norm = self.normalize_game_name(name)
        if not norm: return 999999999
        h = zlib.adler32(norm.encode()) & 0xffffffff
        return 900000000 + (h % 99999999)

    def is_appid_match_plausible(self, query: str, app_id: int) -> bool:
        return True

    def __init__(self, steam_api_key: Optional[str] = None, sgdb_api_key: Optional[str] = STEAMGRIDDB_API_KEY):
        self.api_key = steam_api_key
        self.sgdb = SteamGridDBProvider(sgdb_api_key) if sgdb_api_key else None
        self._cache = {}
        self._save_queue = []
        self._stop_flush = False
        self._semaphore = asyncio.Semaphore(5)
        self._http_client = None

    async def _get_client(self):
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)
        return self._http_client

    def _log(self, msg: str, **kwargs):
        """Log formatado para o SteamClient"""
        print(f"[SteamClient] {msg}")

    def sanitize_search_term(self, text: str) -> str:
        """Limpa termos de busca para melhorar o matching"""
        if not text: return ""
        # Remove caracteres especiais preservando espaços e alfanuméricos básicos
        s = re.sub(r'[^a-zA-Z0-9\s\']', ' ', str(text))
        # Remove espaços duplos
        return " ".join(s.split()).lower()

    async def is_appid_match_plausible_async(self, query: str, app_id: int) -> bool:
        """Versão assíncrona da validação de plausibilidade"""
        if not query or not app_id: return False
        
        # Don't check for very high synthetic IDs
        if app_id >= 900000000: return True

        # 1. TENTATIVA LOCAL: Se o ID está na SteamApp, verificamos o nome lá. 
        # Ganho imenso: evita chamar API só para validar se o ID faz sentido.
        session = get_session()
        try:
            local_app = session.get(SteamApp, int(app_id))
            if local_app:
                return self.is_name_match_plausible(query, local_app.name)
        except Exception as e:
            self._log(f"Erro ao validar plausibilidade local: {e}")
        finally:
            session.close()

        # 2. SE NÃO ESTIVER NA LISTA LOCAL, busca detalhes (pode bater no cache ou API)
        details = await self.get_game_details(app_id)
        if not details: return False
        
        candidate_name = details.get("name", "")
        return self.is_name_match_plausible(query, candidate_name)

    def is_name_match_plausible(self, query: str, candidate_name: str) -> bool:
        """Verifica se o nome encontrado faz sentido para a busca"""
        # USER REQUEST: Bypass strict plausibility checks as they are blocking valid games.
        # We will log low confidence matches but allow them to pass.
        if not query or not candidate_name: return False
        
        q = self.normalize_game_name(query)
        c = self.normalize_game_name(candidate_name)
        
        if q in c or c in q: return True
        
        ratio = difflib.SequenceMatcher(None, q, c).ratio()
        if ratio <= 0.7:
             self._log(f"[Plausibility] Low confidence match allowed ({ratio:.2f}): '{q}' vs '{c}'")
        
        return True

    def _get_from_cache(self, key: str):
        return self._cache.get(key)

    def _set_cache(self, key: str, value: Any):
        self._cache[key] = value

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def start_persistence_loop(self):
        self._log("[SteamService] Iniciando loop de persistência...")
        self._stop_flush = False
        while not self._stop_flush:
            await asyncio.sleep(1)
            await self.flush_metadata()

    async def stop_persistence_loop(self):
        """Força salvamento final."""
        self._stop_flush = True
        await self.flush_metadata()
        self._log("[SteamService] Loop encerrado e flusheado.")

    def clear_queue(self):
        """Limpa a fila de persistência sem salvar."""
        if hasattr(self, "_save_queue"):
            self._save_queue = []
        self._log("[SteamService] Fila de persistência limpa.")

    def clear_cache(self):
        """Limpa o cache em memória."""
        self._cache = {}
        self._log("[SteamService] Cache em memória limpo.")



    async def flush_metadata(self):
        """Sincroniza o buffer com o disco."""
        if not hasattr(self, "_save_queue") or not self._save_queue:
            return

        batch = list(self._save_queue)
        self._save_queue = []
        
        db_path = get_db_file_path()
        size_before = db_path.stat().st_size if db_path.exists() else 0
        
        session = get_session()
        try:
            # Dedup
            unique = {}
            for d in batch:
                aid = d.get("app_id") or d.get("steam_appid") or d.get("appId")
                if aid: unique[int(aid)] = d
            
            processed = 0
            for app_id, details in unique.items():
                try:
                    obj = session.get(GameMetadata, app_id)
                    if not obj:
                        obj = GameMetadata(app_id=app_id)
                    
                    obj.name = details.get("name") or details.get("game_name") or obj.name
                    obj.type = details.get("type") or obj.type
                    for field in ["genres", "developers"]:
                        val = details.get(field)
                        if val: setattr(obj, f"{field}_json", json.dumps(val))
                    
                    obj.header_image_url = details.get("header") or details.get("header_image") or obj.header_image_url
                    obj.capsule_image_url = details.get("capsule") or details.get("capsule_image") or details.get("image") or obj.capsule_image_url
                    obj.updated_at = datetime.now()
                    session.add(obj)
                    processed += 1
                except: continue
                
            session.commit()
            if processed > 0:
                print(f"[SteamService] ✅ FLUSH COMPLETO: {processed} itens. DB: {size_before} bytes")
        except Exception as e:
            print(f"[SteamService] ❌ ERRO NO FLUSH: {e}")
        finally:
            session.close()

    def persist_metadata(self, details: Dict[str, Any], force_flush: bool = True):
        """Salva metadados DIRETAMENTE no banco (Sem Buffer - Modo Seguro)"""
        aid = details.get("app_id") or details.get("steam_appid") or details.get("appId")
        if not aid: return

        # Direct synchronous write
        session = get_session()
        try:
            app_id = int(aid)
            obj = session.get(GameMetadata, app_id)
            if not obj:
                obj = GameMetadata(app_id=app_id)
            
            obj.name = details.get("name") or details.get("game_name") or obj.name
            obj.type = details.get("type") or obj.type
            for field in ["genres", "developers"]:
                val = details.get(field)
                if val: setattr(obj, f"{field}_json", json.dumps(val))
            
            obj.header_image_url = details.get("header") or details.get("header_image") or obj.header_image_url
            obj.capsule_image_url = details.get("capsule") or details.get("capsule_image") or details.get("image") or obj.capsule_image_url
            obj.updated_at = datetime.now()
            
            session.add(obj)
            session.commit()
            # print(f"[DB-SAFE] Salvo imediatamente: {app_id} - {obj.name}")
        except Exception as e:
            print(f"[SteamService] ❌ Erro ao salvar {aid}: {e}")
        finally:
            session.close()

    def get_total_metadata_count(self) -> int:
        session = get_session()
        try:
            statement = select(func.count()).select_from(GameMetadata)
            return int(session.exec(statement).one() or 0)
        except: return 0
        finally: session.close()

    def get_batch_metadata(self, app_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not app_ids: return {}
        ids = [int(aid) for aid in app_ids if aid is not None]
        results_map = {}
        session = get_session()
        try:
            chunk_size = 500
            for i in range(0, len(ids), chunk_size):
                chunk = ids[i:i + chunk_size]
                statement = select(GameMetadata).where(GameMetadata.app_id.in_(chunk))
                for r in session.exec(statement).all():
                    results_map[int(r.app_id)] = {
                        "app_id": int(r.app_id),
                        "genres": json.loads(r.genres_json or "[]"),
                        "developers": json.loads(r.developers_json or "[]"),
                        "name": r.name,
                        "header_image": r.header_image_url,
                        "capsule": r.capsule_image_url
                    }
            return results_map
        finally: session.close()

    async def find_appid_locally(self, query: str) -> Optional[int]:
        """Busca o AppID no banco de dados local (SteamApp)"""
        if not query: return None
        norm = self.normalize_game_name(query)
        session = get_session()
        try:
            # 1. Busca exata pelo nome normalizado
            statement = select(SteamApp.appid).where(SteamApp.normalized_name == norm).limit(5)
            results = session.exec(statement).all()
            if results:
                # Se houver mais de um, por enquanto pegamos o primeiro (geralmente o jogo base tem ID menor ou é o primeiro)
                # O resolver geralmente lida com isso se for o caso.
                return int(results[0])
            
            # 2. Busca exata pelo nome original (case-insensitive)
            statement = select(SteamApp.appid).where(func.lower(SteamApp.name) == query.lower()).limit(1)
            res = session.exec(statement).first()
            if res: return int(res)

            return None
        except Exception as e:
            self._log(f"Erro na busca local de AppID: {e}")
            return None
        finally:
            session.close()

    async def search_monitor(self, query: str, priority: bool = False) -> Optional[int]:
        """Tenta encontrar o AppID para um jogo, priorizando o banco local"""
        # 1. Tentar busca local primeiro (MUITO mais rápido e offline)
        local_id = await self.find_appid_locally(query)
        if local_id:
            self._log(f"AppID encontrado LOCALMENTE para '{query}': {local_id}")
            return local_id

        # 2. Fallback para API do Steam (Original)
        try:
            res = await steam_api_client.search_games(query)
            if res: return int(res[0].get("id"))
        except: pass
        return None

    async def get_game_details(self, app_id: int, priority: bool = False) -> Dict[str, Any]:
        """Busca detalhes do jogo (nome, gêneros, desenvolvedores, imagens).
           Tenta: Cache Memória -> Banco de Dados -> API Steam.
        """
        cache_key = f"details:{app_id}"
        cached = self._get_from_cache(cache_key)
        if cached: 
            return cached
        
        # 1. Tentar Banco de Dados Local (GameMetadata) - Cache Persistente
        session = get_session()
        try:
            obj = session.get(GameMetadata, int(app_id))
            if obj and (obj.header_image_url or obj.capsule_image_url):
                details = {
                    "app_id": int(app_id),
                    "name": obj.name,
                    "developers": json.loads(obj.developers_json or "[]"),
                    "genres": json.loads(obj.genres_json or "[]"),
                    "header": obj.header_image_url,
                    "capsule": obj.capsule_image_url,
                    "type": obj.type
                }
                self._set_cache(cache_key, details)
                self._log(f"[DB-HIT] Metadados recuperados do banco para ID {app_id}")
                return details
        except Exception as e:
            self._log(f"Erro ao ler GameMetadata do banco: {e}")
        finally:
            session.close()

        # 2. Tentar API do Steam (Request Externo)
        self._log(f"[API-REQ] Buscando detalhes na Steam Store para ID {app_id}...")
        async with self._semaphore:
            try:
                client = await self._get_client()
                url = "https://store.steampowered.com/api/appdetails"
                resp = await client.get(url, params={"appids": app_id, "l": "brazilian"}, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if str(app_id) in data and data[str(app_id)].get("success"):
                        app_data = data[str(app_id)]["data"]
                        details = {
                            "app_id": int(app_id),
                            "name": app_data.get("name", ""),
                            "developers": app_data.get("developers", []),
                            "genres": [g.get("description", "") for g in app_data.get("genres", [])],
                            "header": app_data.get("header_image", ""),
                            "capsule": app_data.get("capsule_image", ""),
                            "type": app_data.get("type", "game")
                        }
                        self._set_cache(cache_key, details)
                        # Persiste para o banco para futuras consultas
                        self.persist_metadata(details, force_flush=priority)
                        return details
            except Exception as e:
                self._log(f"Erro ao buscar detalhes do Steam API (AppID {app_id}): {e}")
        return {}

    async def get_game_art(self, query: str, priority: bool = False) -> Dict[str, Any]:
        """Busca arte de um jogo (AppID ou Nome)"""
        if not query: return {"found": False}
        
        # Se for AppID numérico
        if str(query).isdigit():
            aid = int(query)
            details = await self.get_game_details(aid, priority=priority)
            if details:
                return {"found": True, "app_id": aid, **details}
        
        # Se for nome, tenta resolver AppID primeiro
        aid = await self.search_monitor(query, priority=priority)
        if aid:
            details = await self.get_game_details(aid, priority=priority)
            if details:
                return {"found": True, "app_id": aid, **details}
                
        return {"found": False, "app_id": None}

steam_client = SteamClient()
