"""
Steam API Module — Requisições robustas para appdetails, screenshots, vídeos
Implementa timeouts, retries com backoff, e tratamento de erros
"""

import httpx
import asyncio
import time
import locale
import re
import ctypes
from typing import Dict, Optional, List, Any


class SteamAPIClient:
    def __init__(self, timeout: float = 5.0, max_retries: int = 2):
        self._client: Optional[httpx.AsyncClient] = None
        self._timeout = timeout
        self._max_retries = max_retries
        # Cache simples em memória: appId -> (dados_normalizados, timestamp)
        self._cache: Dict[int, tuple[Dict, float]] = {}
        self._cache_ttl = 600  # 10 minutos
        self._language_param = self._get_system_language_param()
        print(f"[SteamAPI] Idioma do sistema detectado: {self._language_param}")

    def _get_system_language_param(self) -> str:
        """
        Detecta o idioma do sistema e mapeia para parametro Steam.
        Tenta usar ctypes no Windows para pegar o idioma de UI real (MUI),
        pois locale.getdefaultlocale() muitas vezes retorna en_US devido a formatação regional.
        """
        lang_code = "english"
        
        # 1. Tentar ctypes no Windows (Mais confiável para UI Language)
        try:
            if hasattr(ctypes, 'windll'):
                windll = ctypes.windll.kernel32
                # GetUserDefaultUILanguage retorna o ID numérico (ex: 1046 para pt-BR)
                lang_id = windll.GetUserDefaultUILanguage()
                
                # Mapeamento de IDs comuns
                # https://learn.microsoft.com/en-us/windows/win32/intl/language-identifier-constants-and-strings
                if lang_id == 1046: return "brazilian" # pt-BR
                if lang_id == 2070: return "portuguese" # pt-PT
                if lang_id == 1034: return "spanish" # es-ES
                if lang_id == 1036: return "french" # fr-FR
                if lang_id == 1031: return "german" # de-DE
                if lang_id == 1040: return "italian" # it-IT
                if lang_id == 1049: return "russian" # ru-RU
                if lang_id == 1041: return "japanese" # ja-JP
                if lang_id == 2052: return "schinese" # zh-CN
                
        except Exception as e:
            print(f"[SteamAPI] Erro ao detectar idioma via ctypes: {e}")

        # 2. Fallback para locale (Linux/Mac ou se ctypes falhar)
        try:
            sys_lang, _ = locale.getdefaultlocale()
            if not sys_lang:
                return "english"
            
            sys_lang = sys_lang.lower()
            if "pt" in sys_lang:
                return "brazilian"
            if "es" in sys_lang:
                return "spanish"
            if "fr" in sys_lang:
                return "french"
            if "de" in sys_lang:
                return "german"
            if "it" in sys_lang:
                return "italian"
            if "ru" in sys_lang:
                return "russian"
            if "ja" in sys_lang:
                return "japanese"
            if "zh" in sys_lang:
                return "schinese"
            
            return "english"
        except:
            return "english"

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
        Implementa estratégia "Dual Fetch" para tradução robusta:
        - Se idioma != english, busca English + Localized simultaneamente.
        - Usa texto do Localized + Assets do English (reparando URLs quebradas).
        """

        # Cache
        if self._is_cache_valid(app_id):
            print(f"[SteamAPI] Cache hit para AppID {app_id}")
            return self._cache[app_id][0]

        print(f"[SteamAPI] Buscando detalhes para AppID {app_id} (Lang: {self._language_param})...")

        for attempt in range(self._max_retries + 1):
            try:
                client = await self._get_client()
                url = "https://store.steampowered.com/api/appdetails"
                
                # Definir tarefas de fetch
                tasks = []
                
                # 1. Fetch Inlgês (Padrão Ouro para Assets)
                tasks.append(client.get(url, params={"appids": app_id, "l": "english"}, timeout=self._timeout))
                
                # 2. Fetch Localizado (se necessario)
                if self._language_param != "english":
                    tasks.append(client.get(url, params={"appids": app_id, "l": self._language_param}, timeout=self._timeout))
                
                # Executar em paralelo
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                resp_en = responses[0]
                resp_loc = responses[1] if len(responses) > 1 else None

                # Verificar resposta em inglês (obrigatória)
                if isinstance(resp_en, Exception):
                    raise resp_en
                
                if resp_en.status_code == 200:
                    data_en = resp_en.json()
                    
                    if str(app_id) in data_en and data_en[str(app_id)].get("success"):
                        app_data_en = data_en[str(app_id)]["data"]
                        
                        # Se tiver dados localizados validos, fazer o merge
                        app_data_final = app_data_en
                        if resp_loc and not isinstance(resp_loc, Exception) and resp_loc.status_code == 200:
                            data_loc = resp_loc.json()
                            if str(app_id) in data_loc and data_loc[str(app_id)].get("success"):
                                app_data_loc = data_loc[str(app_id)]["data"]
                                print(f"[SteamAPI] Mesclando tradução ({self._language_param}) com assets originais...")
                                app_data_final = self._merge_localized_data(app_data_en, app_data_loc)

                        # Extrair e normalizar dados
                        details = self._normalize_appdetails(app_id, app_data_final)
                        
                        # Cachear
                        self._cache[app_id] = (details, time.time())
                        return details
                    else:
                        print(f"[SteamAPI] AppID {app_id} não encontrado ou indisponível")
                        return self._empty_response(app_id)

                elif resp_en.status_code == 429:
                    wait_time = 2 ** attempt
                    print(f"[SteamAPI] Rate limit! Aguardando {wait_time}s antes de retry...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    if attempt < self._max_retries:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return self._empty_response(app_id)

            except asyncio.TimeoutError:
                print(f"[SteamAPI] Timeout na tentativa {attempt + 1}")
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

    def _merge_localized_data(self, data_en: Dict, data_loc: Dict) -> Dict:
        """
        Mescla dados em inglês (base confiavel) com dados localizados (texto).
        Repara URLs de imagem quebradas no HTML localizado usando o inglês como referência.
        """
        merged = data_en.copy()
        
        # Campos de texto seguros para substituir diretamente
        text_fields = [
            "short_description", 
            "supported_languages",
            "header_image", # As vezes a imagem localizada é customizada (ex: logo traduzido)
            "capsule_image",
            "capsule_imagev5"
        ]
        
        for field in text_fields:
            if data_loc.get(field):
                merged[field] = data_loc[field]
                
        # Campos HTML complexos (about_the_game, detailed_description)
        # Precisam de reparo de URLs
        html_fields = ["about_the_game", "detailed_description"]
        
        for field in html_fields:
            if data_loc.get(field):
                html_loc = data_loc[field]
                html_en = data_en.get(field, "")
                
                # Tentar reparar imagens quebradas (src="http...", src="...store_skinny...")
                # Estrategia: Extrair todas as URLs do EN e substituir no LOC na mesma ordem
                try:
                    repaired_html = self._repair_html_images(html_loc, html_en)
                    merged[field] = repaired_html
                except Exception as e:
                    print(f"[SteamAPI] Falha ao reparar HTML do campo {field}: {e}")
                    merged[field] = html_loc # Fallback para original (mesmo que quebrado)

        return merged

    def _repair_html_images(self, html_loc: str, html_en: str) -> str:
        """
        Substitui URLs de imagens "feias/quebradas" do HTML localizado
        pelas URLs limpas do HTML em inglês.
        """
        # Extrair URLs de imagem (src="...")
        # Regex simplificado que pega o conteúdo do src
        url_pattern = r'src=["\']([^"\']+)["\']'
        
        urls_en = re.findall(url_pattern, html_en)
        urls_loc = re.findall(url_pattern, html_loc)
        
        # Se a quantidade de imagens for diferente, é arriscado substituir por índice.
        # Mas geralmente é igual. Se for diferente, tentamos substituir apenas as que parecem quebradas.
        if len(urls_en) == len(urls_loc) and len(urls_en) > 0:
            # Substituição cirúrgica
            # Vai iterar sobre as URLs localizadas e substituir no HTML original
            # Cuidado para não substituir a string errada se houver duplicatas
            
            # Abordagem melhor: reconstruir o HTML? Não, muito difícil sem parser.
            # Abordagem de substituição sequencial:
            # Vamos quebrar o HTML localizado pelos matches e reconstruir intercalando com as URLs EN.
            
            parts = re.split(url_pattern, html_loc)
            # parts[0] + urls_loc[0] + parts[1] + ...
            # O split retorna: [texto_antes, url_capturada, texto_depois, url_capturada, ...]
            
            new_html = []
            for i, part in enumerate(parts):
                new_html.append(part)
                # Se for uma posição ímpar, é onde estava uma URL (no split do re com grupo de captura)
                # O re.split com capturing group inclui os matches na lista.
                # parts[0] = texto antes
                # parts[1] = url match 1
                # parts[2] = texto entre 1 e 2
                
                # Mas espera, re.split coloca o separator na lista. 
                # Se eu tenho N urls, eu tenho 2N+1 elementos?
                # Ex: "img src='A' end" -> split -> ["img src='", "A", "' end"]
                pass 
                
            # Simplificando: Apenas rodar um sub com callback que usa um iterador das URLs EN
            iter_en = iter(urls_en)
            
            def replace_match(match):
                try:
                    new_url = next(iter_en)
                    # Forçar HTTPS se vier http
                    if new_url.startswith("http:"):
                        new_url = new_url.replace("http:", "https:")
                    return f'src="{new_url}"'
                except StopIteration:
                    return match.group(0) # Acabou as do EN, mantem original
            
            return re.sub(r'src=["\']([^"\']+)["\']', replace_match, html_loc)
            
        return html_loc


    def _replace_steam_placeholders(self, html_content: str, app_id: int) -> str:
        """Substitui placeholders do HTML da Steam por URLs reais."""
        if not html_content:
            return html_content
        
        # Substituir {STEAM_APP_IMAGE} pela URL base da CDN da Steam
        steam_app_image_url = f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}"
        html_content = html_content.replace("{STEAM_APP_IMAGE}", steam_app_image_url)
        
        # Outros placeholders comuns da Steam
        html_content = html_content.replace("{STEAM_CLAN_IMAGE}", "https://cdn.akamai.steamstatic.com/steamcommunity/public/images/clans")
        html_content = html_content.replace("{STEAM_CLAN_LOC_IMAGE}", "https://cdn.akamai.steamstatic.com/steamcommunity/public/images/clans")
        
        # FIX: Limpar URLs malformadas que podem causar erro no frontend (ex: /src=https:...)
        # Algumas vezes a Steam ou o parser pode deixar lixo no src
        import re
        
        def fix_src(match):
            src = match.group(1)
            # Remove prefixo /src= ou src= se existir (erro comum de parseamento)
            if "/src=" in src:
                src = src.replace("/src=", "")
            if "src=" in src:
                src = src.replace("src=", "")
            
            # Se a URL ficou relativa ou quebrada, tentar consertar
            if src.startswith("//"):
                src = "https:" + src
            
            return f'src="{src}"'

        # Substituir src="..." por versão limpa
        html_content = re.sub(r'src=["\']([^"\']+)["\']', fix_src, html_content)

        return html_content

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

                # NOVO: Steam agora usa HLS streaming (hls_h264) para vídeos modernos
                # Prioridade: hls_h264 > webm.max > mp4.max > webm.480 > mp4.480
                
                # Tentar HLS primeiro (formato moderno com áudio)
                hls_h264 = movie.get("hls_h264")
                if hls_h264:
                    movie_obj["hls"] = hls_h264
                    movie_obj["format"] = "hls"
                
                # Fallback para formatos legados (webm/mp4)
                webm = movie.get("webm")
                if isinstance(webm, dict):
                    # Priorizar 'max' (melhor qualidade) sobre '480' (comprimido/sem áudio)
                    movie_obj["webm"] = webm.get("max") or webm.get("480") or ""

                mp4 = movie.get("mp4")
                if isinstance(mp4, dict):
                    movie_obj["mp4"] = mp4.get("max") or mp4.get("480") or ""

                # Filtrar microtrailers (vídeos de hover sem som)
                mp4_url = movie_obj.get("mp4", "")
                webm_url = movie_obj.get("webm", "")
                hls_url = movie_obj.get("hls", "")
                
                if "microtrailer" in str(mp4_url) or "microtrailer" in str(webm_url) or "microtrailer" in str(hls_url):
                    continue

                # Adicionar se tiver pelo menos uma URL válida
                if hls_url or mp4_url or webm_url:
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

        # Extended Metadata (processar placeholders em campos HTML)
        pc_requirements = app_data.get("pc_requirements", {})
        if isinstance(pc_requirements, dict):
            if "minimum" in pc_requirements:
                pc_requirements["minimum"] = self._replace_steam_placeholders(pc_requirements["minimum"], app_id)
            if "recommended" in pc_requirements:
                pc_requirements["recommended"] = self._replace_steam_placeholders(pc_requirements["recommended"], app_id)
        
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
            "description_long": self._replace_steam_placeholders(app_data.get("detailed_description", ""), app_id),
            "genres": genres,
            "categories": categories,
            "developers": app_data.get("developers", []),
            "publishers": app_data.get("publishers", []),
            "price": app_data.get("price_overview", {}).get("final_formatted", "Free"),
            "metacritic_score": app_data.get("metacritic", {}).get("score"),
            "website": app_data.get("website", ""),
            "support_url": app_data.get("support_info", {}).get("url", ""),
            "release_date": app_data.get("release_date", {}).get("date", ""),
            # Extended Metadata
            "supported_languages": app_data.get("supported_languages", ""),
            "pc_requirements": pc_requirements,
            "mac_requirements": app_data.get("mac_requirements", {}),
            "linux_requirements": app_data.get("linux_requirements", {}),
            "legal_notice": app_data.get("legal_notice", ""),
            "controller_support": self._extract_controller_support(app_data.get("categories", []), app_data.get("controller_support", "")),
            "about_the_game": self._replace_steam_placeholders(app_data.get("about_the_game", ""), app_id),
        }

    def _extract_controller_support(self, categories: List[Dict], raw_support: str) -> str:
        """Extrai nível de suporte a controle (full, partial, none)."""
        # 1. Tentar campo direto (nova API)
        if raw_support:
            return raw_support

        # 2. Tentar via categorias (legacy)
        # 28 = Full controller support, 18 = Partial controller support
        cat_ids = [c.get("id") for c in categories]
        if 28 in cat_ids:
            return "full"
        if 18 in cat_ids:
            return "partial"
        
        return "none"

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