"""
Details Controller — Monta payload completo para página de detalhes
Integra Steam API, SteamGridDB e resolver
Implementa regras de prioridade e fallbacks
"""

from typing import Dict, Any, Optional
from backend.steam_api import steam_api_client
from backend.steam_service import steam_client
from backend.resolver import resolve_game_images

class GameDetailsController:
    """
    Controlador que orquestra a busca de detalhes completos do jogo
    Integra múltiplas fontes com fallback robusto
    """
    
    async def get_game_details(self, app_id: Optional[int] = None, game_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Busca detalhes completos do jogo
        
        Entrada:
        - app_id: AppID da Steam (preferencial)
        - game_name: Nome do jogo (fallback para resolver AppID)
        
        Saída:
        - Payload completo com imagens, vídeos, descrição, metadados
        """
        
        requested_name = game_name
        resolved_name = game_name

        # Se não tem app_id, tenta resolver pelo nome
        if not app_id and game_name:
            candidates = self._build_name_candidates(game_name)
            print(f"[DetailsController] Resolvendo AppID para '{game_name}'...")
            for candidate in candidates:
                app_id = await self._resolve_app_id(candidate)
                if app_id:
                    resolved_name = candidate
                    break
        
        # Se conseguiu app_id, buscar na Steam
        if app_id:
            print(f"[DetailsController] Buscando detalhes da Steam para AppID {app_id}...")
            steam_details = await steam_api_client.get_appdetails(app_id)
            
            if steam_details.get("found"):
                # Enriquecer com imagens de alta qualidade (resolver)
                print(f"[DetailsController] Resolvendo imagens de alta qualidade...")
                image_data = await resolve_game_images(resolved_name or steam_details.get("name", ""))
                
                # Mesclar dados
                result = self._merge_details(steam_details, image_data)
                return result
        
        # Se chegou aqui, Steam falhou ou não tem app_id
        # Tentar SteamGridDB como fallback
        if game_name:
            candidates = self._build_name_candidates(game_name)
            resolved_name = resolved_name or game_name
            print(f"[DetailsController] Steam falhou/indisponível, tentando SteamGridDB para '{resolved_name}'...")
            return await self._get_from_steamgriddb(candidates, app_id)
        
        return self._error_response("app_id_not_found", "Não foi possível resolver o AppID")
    
    def _build_name_candidates(self, raw_name: str) -> list[str]:
        """Build a prioritized list of candidate names for search/lookup."""
        out: list[str] = []
        raw = (raw_name or "").strip()
        if not raw:
            return out

        # Prefer base title before ':' when present (common in release names).
        if ":" in raw:
            left = raw.split(":", 1)[0].strip()
            left_clean = steam_client.sanitize_search_term(left)
            if left_clean:
                out.append(left_clean)

        clean = steam_client.sanitize_search_term(raw)
        if clean:
            out.append(clean)

        # Fallbacks: reduce word count (helps when suffixes like 'The Mercenaries Edition' mislead).
        words = clean.split() if clean else []
        if len(words) >= 2:
            out.append(" ".join(words[:2]))
        if words:
            out.append(words[0])

        # De-dup while preserving order
        seen = set()
        uniq: list[str] = []
        for s in out:
            key = s.lower().strip()
            if key and key not in seen:
                seen.add(key)
                uniq.append(s)
        return uniq

    async def _resolve_app_id(self, game_name: str) -> Optional[int]:
        """Resolve AppID a partir do nome do jogo"""
        try:
            app_id = await steam_client.search_monitor(game_name)
            return app_id
        except Exception as e:
            print(f"[DetailsController] Erro ao resolver AppID: {e}")
            return None
    
    async def _get_from_steamgriddb(self, game_names: list[str], app_id: Optional[int] = None) -> Dict[str, Any]:
        """Fallback para SteamGridDB quando Steam não tem dados"""
        try:
            if steam_client.sgdb:
                print(f"[DetailsController] Buscando em SteamGridDB...")
                for candidate in (game_names or []):
                    sgdb_data = await steam_client.sgdb.search_and_get_art(candidate)
                    if sgdb_data:
                        return {
                            "found": True,
                            "app_id": app_id,
                            "name": candidate,
                            "header_image": sgdb_data.get("header", ""),
                            "capsule": sgdb_data.get("capsule", ""),
                            "background": sgdb_data.get("background", ""),
                            "screenshots": [],
                            "movies": [],
                            "description_short": "Informações disponíveis apenas no SteamGridDB",
                            "description_long": "",
                            "genres": [],
                            "categories": [],
                            "developers": [],
                            "publishers": [],
                            "release_date": "",
                            "price": "",
                            "metacritic_score": None,
                            "website": "",
                            "support_url": "",
                            "source": "steamgriddb"
                        }
        except Exception as e:
            print(f"[DetailsController] Erro ao buscar SteamGridDB: {e}")
        
        return self._error_response("all_sources_failed", "Não foi possível encontrar detalhes do jogo")
    
    def _merge_details(self, steam_details: Dict, image_data: Dict) -> Dict[str, Any]:
        """
        Mescla dados da Steam com imagens resolvidas
        Prioriza imagens de alta qualidade do resolver
        """
        result = steam_details.copy()
        
        # Sobrescrever imagens com as resolvidas (melhor qualidade)
        if image_data.get("found"):
            result["header_image"] = image_data.get("header") or result.get("header_image", "")
            result["capsule"] = image_data.get("capsule") or result.get("capsule", "")
            result["background"] = image_data.get("background") or result.get("background", "")
            result["hero_image"] = image_data.get("hero", "")
            result["logo_image"] = image_data.get("logo", "")
        
        # Garantir que temos pelo menos um screenshot (usar header como fallback)
        if not result.get("screenshots") and result.get("header_image"):
            result["screenshots"] = [result["header_image"]]
        
        # Adicionar metadados de resolução
        result["resolved_at"] = __import__("datetime").datetime.now().isoformat()
        
        return result
    
    def _error_response(self, error_code: str, message: str) -> Dict[str, Any]:
        """Resposta de erro padronizada"""
        return {
            "found": False,
            "error": error_code,
            "error_message": message,
            "app_id": None,
            "name": "",
            "header_image": "",
            "capsule": "",
            "background": "",
            "screenshots": [],
            "movies": [],
            "description_short": "",
            "description_long": "",
            "genres": [],
            "categories": [],
            "developers": [],
            "publishers": [],
            "release_date": "",
            "price": "",
            "metacritic_score": None,
            "website": "",
            "support_url": "",
        }


# Instância global
details_controller = GameDetailsController()
