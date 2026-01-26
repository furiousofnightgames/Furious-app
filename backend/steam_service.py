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
from backend.models.models import GameMetadata
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
        s = re.sub(r'[\(\[].*?[\)\]]', '', s)
        s = re.sub(r'(?i)\bv\d+(\.\d+)*\b', '', s)
        s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
        return " ".join(s.split()).lower()

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

        details = await self.get_game_details(app_id)
        if not details: return False
        
        candidate_name = details.get("name", "")
        return self.is_name_match_plausible(query, candidate_name)

    def is_name_match_plausible(self, query: str, candidate_name: str) -> bool:
        """Verifica se o nome encontrado faz sentido para a busca"""
        if not query or not candidate_name: return False
        
        q = self.normalize_game_name(query)
        c = self.normalize_game_name(candidate_name)
        
        if q in c or c in q: return True
        
        # Fuzzy matching básico se necessário
        ratio = difflib.SequenceMatcher(None, q, c).ratio()
        return ratio > 0.7

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
            await asyncio.sleep(3)
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

    def persist_metadata(self, details: Dict[str, Any], force_flush: bool = False):
        if not hasattr(self, "_save_queue"):
            self._save_queue = []
        aid = details.get("app_id") or details.get("steam_appid") or details.get("appId")
        if not aid: return
        self._save_queue.append(details)
        print(f"[BUFFER-IN] Item {aid} na fila. Pendentes: {len(self._save_queue)}")
        if force_flush:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running(): loop.create_task(self.flush_metadata())
            except: pass

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

    async def search_monitor(self, query: str, priority: bool = False) -> Optional[int]:
        """Tenta encontrar o AppID para um jogo"""
        # Implementação básica usando o client de API para manter compatibilidade
        try:
            # Note: steam_api_client.search_games deve ser restaurado/existir se o usuário espera que funcione
            res = await steam_api_client.search_games(query)
            if res: return int(res[0].get("id"))
        except: pass
        return None

    async def get_game_details(self, app_id: int, priority: bool = False) -> Dict[str, Any]:
        cache_key = f"details:{app_id}"
        cached = self._get_from_cache(cache_key)
        if cached: return cached
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
                            "app_id": app_id,
                            "name": app_data.get("name", ""),
                            "developers": app_data.get("developers", []),
                            "genres": [g.get("description", "") for g in app_data.get("genres", [])],
                            "header": app_data.get("header_image", ""),
                            "capsule": app_data.get("capsule_image", "")
                        }
                        self._set_cache(cache_key, details)
                        self.persist_metadata(details, force_flush=priority)
                        return details
            except: pass
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
