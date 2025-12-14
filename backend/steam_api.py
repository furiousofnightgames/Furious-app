"""
Steam API Module — Requisições robustas para appdetails, screenshots, vídeos
Implementa timeouts, retries com backoff, e tratamento de erros
"""

import httpx
import asyncio
import time
from typing import Dict, Optional, List, Any


class SteamAPIClient:
    def __init__(self, timeout: float = 5.0, max_retries: int = 2):
        self._client: Optional[httpx.AsyncClient] = None
        self._timeout = timeout
        self._max_retries = max_retries
        # Cache simples em memória: appId -> (dados_normalizados, timestamp)
        self._cache: Dict[int, tuple[Dict, float]] = {}
        self._cache_ttl = 600  # 10 minutos

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self._timeout, follow_redirects=True)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _is_cache_valid(self, app_id: int) -> bool:
        """Verifica se cache ainda é válido para um app_id."""
        if app_id not in self._cache:
            return False
        _, timestamp = self._cache[app_id]
        return (time.time() - timestamp) < self._cache_ttl

    def clear_cache(self):
        """Limpa todo o cache de API"""
        self._cache.clear()
        print("[SteamAPI] Cache limpo")

    async def get_appdetails(self, app_id: int) -> Dict[str, Any]:
        """
        Busca detalhes completos do jogo na Steam API.

        Retorna dados já normalizados:
        - imagens (header, capsule, background)
        - screenshots
        - movies (com URLs mp4/webm)
        - descrição curta/longa
        - gêneros, categorias
        - devs, publishers, data de lançamento, preço, metacritic, site, suporte
        """

        # Cache
        if self._is_cache_valid(app_id):
            print(f"[SteamAPI] Cache hit para AppID {app_id}")
            return self._cache[app_id][0]

        print(f"[SteamAPI] Buscando detalhes para AppID {app_id}...")

        for attempt in range(self._max_retries + 1):
            try:
                client = await self._get_client()
                url = "https://store.steampowered.com/api/appdetails"
                # Idioma PT-BR (código "brazilian" na Steam)
                params = {"appids": app_id, "l": "brazilian"}

                resp = await client.get(url, params=params, timeout=self._timeout)

                if resp.status_code == 200:
                    data = resp.json()

                    if str(app_id) in data and data[str(app_id)].get("success"):
                        app_data = data[str(app_id)]["data"]

                        # Extrair e normalizar dados
                        details = self._normalize_appdetails(app_id, app_data)

                        # Cachear
                        self._cache[app_id] = (details, time.time())

                        try:
                            print(f"[SteamAPI] OK Detalhes obtidos para AppID {app_id}")
                        except:
                            pass
                        return details
                    else:
                        print(f"[SteamAPI] AppID {app_id} não encontrado ou indisponível")
                        return self._empty_response(app_id)

                elif resp.status_code == 429:
                    # Rate limit — aguardar e tentar de novo
                    wait_time = 2 ** attempt
                    print(f"[SteamAPI] Rate limit! Aguardando {wait_time}s antes de retry...")
                    await asyncio.sleep(wait_time)
                    continue

                else:
                    print(f"[SteamAPI] Status {resp.status_code} para AppID {app_id}")
                    if attempt < self._max_retries:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return self._empty_response(app_id)

            except asyncio.TimeoutError:
                print(f"[SteamAPI] Timeout na tentativa {attempt + 1}/{self._max_retries + 1}")
                if attempt < self._max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return self._empty_response(app_id)

            except Exception as e:
                print(f"[SteamAPI] Erro na tentativa {attempt + 1}: {e}")
                if attempt < self._max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return self._empty_response(app_id)

        return self._empty_response(app_id)

    def _normalize_appdetails(self, app_id: int, app_data: Dict) -> Dict[str, Any]:
        """Normaliza resposta da Steam API, extraindo apenas campos relevantes."""

        # Screenshots
        screenshots: List[str] = []
        if "screenshots" in app_data:
            for ss in app_data["screenshots"][:10]:  # Limitar a 10
                path = ss.get("path_full")
                if path:
                    screenshots.append(path)

        # Vídeos / trailers
        movies: List[Dict[str, Any]] = []
        if "movies" in app_data:
            for movie in app_data["movies"][:5]:  # Limitar a 5
                movie_obj: Dict[str, Any] = {
                    "id": movie.get("id"),
                    "name": movie.get("name", "Trailer"),
                    "thumbnail": movie.get("thumbnail", ""),
                }

                # URLs de vídeo - PRIORIDADE para 'max' (melhor qualidade e áudio) vs '480' (muito comprimido)
                webm = movie.get("webm")
                if isinstance(webm, dict):
                    movie_obj["webm"] = webm.get("max") or webm.get("480") or ""

                mp4 = movie.get("mp4")
                if isinstance(mp4, dict):
                    movie_obj["mp4"] = mp4.get("max") or mp4.get("480") or ""

                # Filtrar microtrailers (videos de hover sem som)
                mp4_url = movie_obj.get("mp4", "")
                webm_url = movie_obj.get("webm", "")
                
                if "microtrailer" in str(mp4_url) or "microtrailer" in str(webm_url):
                    continue

                if mp4_url or webm_url:
                    movies.append(movie_obj)
        
        # Se não achou vídeos na API, tentar extrair do HTML da description_long
        if not movies:
            movies = self._extract_videos_from_html(app_data.get("detailed_description", ""))

        # Gêneros
        genres: List[str] = []
        if "genres" in app_data:
            genres = [g.get("description", "") for g in app_data["genres"] if g.get("description")]

        # Categorias
        categories: List[str] = []
        if "categories" in app_data:
            categories = [c.get("description", "") for c in app_data["categories"] if c.get("description")]

        # Montar resposta normalizada
        return {
            "found": True,
            "app_id": app_id,
            "type": app_data.get("type", ""),
            "name": app_data.get("name", ""),
            "header_image": app_data.get("header_image", ""),
            "capsule": app_data.get("capsule_image", ""),
            "capsule_large": app_data.get("capsule_imagev5", ""),
            "background": app_data.get("background", ""),
            "screenshots": screenshots,
            "movies": movies,
            "description_short": app_data.get("short_description", ""),
            # Manter descrição longa completa para extrair vídeos do HTML
            "description_long": app_data.get("detailed_description", ""),
            "genres": genres,
            "categories": categories,
            "developers": app_data.get("developers", []),
            "publishers": app_data.get("publishers", []),
            "release_date": app_data.get("release_date", {}).get("date", ""),
            "price": app_data.get("price_overview", {}).get("final_formatted", "Free"),
            "metacritic_score": app_data.get("metacritic", {}).get("score"),
            "website": app_data.get("website", ""),
            "support_url": app_data.get("support_info", {}).get("url", ""),
        }

    def _extract_videos_from_html(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extrai URLs de vídeo do HTML da descrição.
        Procura por padrões de <video> tags e URLs .mp4/.webm.
        Suporta múltiplas <source> tags dentro de <video>.
        Tenta converter .webm para .mp4 automaticamente.
        """
        import re
        
        movies: List[Dict[str, Any]] = []
        
        if not html_content:
            return movies
        
        # Padrão: procurar por <video>...</video> blocks
        video_blocks = re.findall(r'<video[^>]*>.*?</video>', html_content, re.DOTALL)
        
        for block_idx, video_block in enumerate(video_blocks[:3]):  # Limitar a 3 vídeos
            movie_obj: Dict[str, Any] = {
                "id": block_idx,
                "name": f"Trailer {block_idx + 1}",
                "thumbnail": "",
                "mp4": "",
                "webm": "",
            }
            
            # Extrair poster (thumbnail) da tag <video>
            poster_match = re.search(r'poster=["\']([^"\']+)["\']', video_block)
            if poster_match:
                movie_obj["thumbnail"] = poster_match.group(1).strip()
            
            # Extrair URLs de <source> tags
            source_tags = re.findall(r'<source[^>]*src=["\']([^"\']+)["\'][^>]*>', video_block)
            
            for src_url in source_tags:
                src_url = src_url.strip()
                if not src_url or not ("http" in src_url or src_url.startswith("/")):
                    continue
                
                # Determinar tipo (mp4 ou webm)
                if ".mp4" in src_url.lower():
                    movie_obj["mp4"] = src_url
                elif ".webm" in src_url.lower():
                    movie_obj["webm"] = src_url
            
            # CRÍTICO: Se tiver WebM mas não MP4, converter WebM para MP4
            # A Steam fornece ambas as versões no mesmo padrão de URL
            if movie_obj["webm"] and not movie_obj["mp4"]:
                mp4_url = movie_obj["webm"].replace(".webm", ".mp4")
                movie_obj["mp4"] = mp4_url
                try:
                    print(f"[SteamAPI] Convertido WebM para MP4")
                except:
                    pass
            
            # Só adicionar se tiver pelo menos uma URL de vídeo
            # PRIORIDADE: mp4 (tem áudio, compatível com PyQt5) > webm (fallback)
            if movie_obj["mp4"] or movie_obj["webm"]:
                movies.append(movie_obj)
        
        # Debug: log das URLs extraídas (completas)
        if movies:
            print(f"[SteamAPI] Extraídos {len(movies)} vídeo(s) do HTML")
            for m in movies:
                mp4_url = m.get('mp4', '') or 'N/A'
                webm_url = m.get('webm', '') or 'N/A'
                print(f"  - {m['name']}:")
                print(f"    mp4:  {mp4_url}")
                print(f"    webm: {webm_url}")
        
        return movies

    def _empty_response(self, app_id: int) -> Dict[str, Any]:
        """Resposta vazia quando não conseguir dados da Steam."""
        return {
            "found": False,
            "app_id": app_id,
            "error": "not_found_or_unavailable",
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


# Instância global usada pelo details_controller
steam_api_client = SteamAPIClient(timeout=5.0, max_retries=2)