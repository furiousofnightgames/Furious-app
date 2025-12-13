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
        
        # Se não tem app_id, tenta resolver pelo nome
        if not app_id and game_name:
            print(f"[DetailsController] Resolvendo AppID para '{game_name}'...")
            app_id = await self._resolve_app_id(game_name)
        
        # Se conseguiu app_id, buscar na Steam
        if app_id:
            print(f"[DetailsController] Buscando detalhes da Steam para AppID {app_id}...")
            steam_details = await steam_api_client.get_appdetails(app_id)
            
            if steam_details.get("found"):
                # Enriquecer com imagens de alta qualidade (resolver)
                print(f"[DetailsController] Resolvendo imagens de alta qualidade...")
                image_data = await resolve_game_images(game_name or steam_details.get("name", ""))
                
                # Mesclar dados
                result = self._merge_details(steam_details, image_data)
                return result
        
        # Se chegou aqui, Steam falhou ou não tem app_id
        # Tentar SteamGridDB como fallback
        if game_name:
            print(f"[DetailsController] Steam falhou/indisponível, tentando SteamGridDB para '{game_name}'...")
            return await self._get_from_steamgriddb(game_name, app_id)
        
        return self._error_response("app_id_not_found", "Não foi possível resolver o AppID")
    
    async def _resolve_app_id(self, game_name: str) -> Optional[int]:
        """Resolve AppID a partir do nome do jogo"""
        try:
            app_id = await steam_client.search_monitor(game_name)
            return app_id
        except Exception as e:
            print(f"[DetailsController] Erro ao resolver AppID: {e}")
            return None
    
    async def _get_from_steamgriddb(self, game_name: str, app_id: Optional[int] = None) -> Dict[str, Any]:
        """Fallback para SteamGridDB quando Steam não tem dados"""
        try:
            if steam_client.sgdb:
                print(f"[DetailsController] Buscando em SteamGridDB...")
                sgdb_data = await steam_client.sgdb.search_and_get_art(game_name)
                
                if sgdb_data:
                    return {
                        "found": True,
                        "app_id": app_id,
                        "name": game_name,
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
