import asyncio
import httpx
from typing import Optional, Dict, List
import abc

# Abstract Base Class for Image Providers
class ImageProvider(abc.ABC):
    @abc.abstractmethod
    async def search_and_get_art(self, query: str) -> Optional[Dict[str, str]]:
        """
        Receives a game name query.
        Returns a dictionary with image URLs (header, capsule, hero, logo, background) or None.
        """
        pass

# Steam Provider (Refactored wrapper around existing logic - to be fully moved later)
# For now, we will keep steam_service doing its thing and just call it from here if needed, 
# or makes this the orchestrator.

# SteamGridDB Provider
class SteamGridDBProvider(ImageProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.steamgriddb.com/api/v2"
        self.client = httpx.AsyncClient(headers={"Authorization": f"Bearer {api_key}"}, timeout=10.0)

    async def search_and_get_art(self, query: str) -> Optional[Dict[str, str]]:
        if not self.api_key or "YOUR_KEY" in self.api_key:
            return None
            
        print(f"[SteamGridDB] Searching for: {query}")
        try:
            # 1. Search for Game ID
            search_resp = await self.client.get(f"{self.base_url}/search/autocomplete/{query}")
            if search_resp.status_code != 200:
                print(f"[SteamGridDB] Search failed: {search_resp.status_code}")
                return None
            
            data = search_resp.json()
            if not data.get("success") or not data.get("data"):
                return None
                
            game_id = data["data"][0]["id"]
            game_name = data["data"][0]["name"]
            print(f"[SteamGridDB] Found Game: {game_name} (ID: {game_id})")
            
            # 2. Fetch Assets (Grids, Heroes, Logos)
            # Parallel requests (compatible with Python 3.10)
            t_grids = asyncio.create_task(self.client.get(f"{self.base_url}/grids/game/{game_id}?dimensions=600x900,460x215&styles=alternate,blurred,material"))
            t_heroes = asyncio.create_task(self.client.get(f"{self.base_url}/heroes/game/{game_id}"))
            t_logos = asyncio.create_task(self.client.get(f"{self.base_url}/logos/game/{game_id}"))

            grids = (await t_grids).json().get("data", [])
            heroes = (await t_heroes).json().get("data", [])
            logos = (await t_logos).json().get("data", [])
            
            def get_url(items):
                return items[0]["url"] if items else None

            # Map to our standard format
            # SteamGridDB "grid" 600x900 -> equivalent to capsule/header logic but different aspect ratio
            # We map "hero" -> "hero" & "background"
            # We map "logo" -> "logo"
            
            hero_url = get_url(heroes)
            logo_url = get_url(logos)
            
            # Grids come in many shapes. 
            # 460x215 is closest to Steam "header"
            # 600x900 is vertical capsule
            
            header_url = None
            capsule_url = None
            
            header_url = None
            capsule_url = None
            
            # Tentar encontrar dimensões exatas primeiro
            for g in grids:
                if g["width"] == 460 and g["height"] == 215:
                    header_url = g["url"]
                if g["width"] == 600 and g["height"] == 900:
                    capsule_url = g["url"]
            
            # Se não achou exato, pega qualquer um disponível como fallback
            if not header_url and grids:
                 header_url = grids[0]["url"]
            if not capsule_url and grids:
                 capsule_url = grids[0]["url"]

            return {
                "header": header_url or hero_url,
                "capsule": capsule_url or header_url,
                "hero": hero_url,
                "logo": logo_url,
                "background": hero_url # SGDB doesnt have specific backgrounds usually, heroes work
            }

        except Exception as e:
            print(f"[SteamGridDB] Error: {e}")
            return None

# Orchestrator
class ImageService:
    def __init__(self, steam_client_instance, sgdb_key: Optional[str] = None):
        self.steam = steam_client_instance
        self.sgdb = SteamGridDBProvider(sgdb_key) if sgdb_key else None
        
    async def get_art(self, query: str) -> Dict[str, Optional[str]]:
        # 1. Try Steam (Fast, Local)
        # We assume steam_client has its own caching logic
        steam_res = await self.steam.get_game_art(query)
        
        # If Steam found an AppID, it returns populated URLs.
        # If not found, app_id is None or 0.
        if steam_res.get("app_id"):
            return steam_res
            
        # 2. Try Fallback (SteamGridDB)
        if self.sgdb:
            print(f"[ImageService] Steam failed for '{query}'. Trying SteamGridDB...")
            sgdb_res = await self.sgdb.search_and_get_art(query)
            if sgdb_res:
                # Merge with empty steam struct but keep structure
                steam_res.update(sgdb_res)
                return steam_res
        else:
             print(f"[ImageService] Steam failed for '{query}' and no SGDB Key configured.")

        return steam_res
