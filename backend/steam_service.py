import httpx
import asyncio
import time
import json
import os
import re
import difflib
from typing import Dict, Optional, Any, List, Set, Tuple

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
        _default_dir = os.path.join(_local_app_data, "furious-app")
        os.makedirs(_default_dir, exist_ok=True)
        APP_LIST_FILE = os.path.join(_default_dir, "steam_applist.json")
    else:
        APP_LIST_FILE = "steam_applist.json"
APP_LIST_URL_OFFICIAL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
APP_LIST_URL_FALLBACK = "https://raw.githubusercontent.com/dgibbs64/SteamCMD-AppID-List/main/steamcmd_appid.json"

from backend.config import STEAMGRIDDB_API_KEY
from backend.image_service import SteamGridDBProvider

class SteamClient:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 3600 * 24  # 24h para artes e buscas
        self._semaphore = asyncio.Semaphore(5)
        self._client: Optional[httpx.AsyncClient] = None
        
        # --- AppList & Search Index ---
        self._app_list: List[Dict] = []
        self._app_index: Dict[str, Set[int]] = {}
        self._app_map: Dict[int, str] = {} # ID -> Name
        self._app_list_loaded = False
        self._app_list_loaded = False
        self._loading_lock = asyncio.Lock()
        
        # --- Fallback Provider ---
        self.sgdb = SteamGridDBProvider(STEAMGRIDDB_API_KEY) if STEAMGRIDDB_API_KEY else None
        if self.sgdb:
            print(f"[SteamService] SteamGridDB ativado como fallback (Key configurada).")
        else:
            print(f"[SteamService] SteamGridDB inativo (Falta STEAMGRIDDB_API_KEY). Apenas jogos da Steam terão imagens.")

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # =========================================================================
    #  APP LIST MANAGEMENT (Local "Hydra-like" Database)
    # =========================================================================
    
    async def ensure_app_list(self):
        """
        Garante que a lista de apps da Steam esteja carregada e indexada em memória.
        Faz download se não existir ou estiver velha.
        """
        if self._app_list_loaded:
            return

        async with self._loading_lock:
            if self._app_list_loaded:
                return

            print(f"[SteamService] AppList cache path: {APP_LIST_FILE}")
            
            # Tentar carregar do disco
            data = await self._load_from_disk()
            
            # Se não tem ou é velho (> 24h), baixa
            if not data:
                print("[SteamService] AppList local ausente ou antigo. Iniciando download...")
                data = await self._download_app_list()
                if data:
                    await self._save_to_disk(data)
            
            if data:
                self._build_index(data)
                self._app_list_loaded = True
                print(f"[SteamService] Índice de busca local pronto! {len(self._app_map)} jogos indexados.")
            else:
                print("[SteamService] FALHA CRÍTICA: Não foi possível carregar AppList. Busca funcionará apenas via API (lenta).")

    async def _load_from_disk(self) -> Optional[List[Dict]]:
        if not os.path.exists(APP_LIST_FILE):
            return None
        
        try:
            # Checar idade do arquivo (24h)
            mtime = os.path.getmtime(APP_LIST_FILE)
            if time.time() - mtime > 86400:
                print("[SteamService] Cache local expirado.")
                return None # Expirado
                
            # Ler arquivo de forma não bloqueante (em thread separada pois é IO)
            def read():
                with open(APP_LIST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            
            data = await asyncio.to_thread(read)
            return data.get("applist", {}).get("apps", [])
        except Exception as e:
            print(f"[SteamService] Erro ao ler cache local: {e}")
            return None

    async def _download_app_list(self) -> Optional[List[Dict]]:
        client = await self._get_client()
        
        async def try_download(url, name, params=None, headers=None):
            try:
                print(f"[SteamService] Baixando AppList via {name} ({url})...")
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                # Normalizar estrutura
                if "applist" in data and "apps" in data["applist"]:
                    return data["applist"]["apps"]
                if "apps" in data:
                    return data["apps"]
                if isinstance(data, list):
                    return data
                    
                print(f"[SteamService] Formato JSON inválido em {name}.")
                return None
            except Exception as e:
                print(f"[SteamService] Falha ao baixar de {name}: {e}")
                return None

        # 1. Tentar Oficial
        apps = await try_download(
            APP_LIST_URL_OFFICIAL,
            "Steam Oficial",
            params={"format": "json"},
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if apps:
            return apps

        apps = await try_download(
            "https://api.steampowered.com/ISteamApps/GetAppList/v2",
            "Steam Oficial (alt)",
            params={"format": "json"},
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if apps:
            return apps
            
        # 2. Tentar Fallback
        print("[SteamService] Tentando servidor mirror (DGibbs)...")
        apps = await try_download(APP_LIST_URL_FALLBACK, "GitHub Mirror")
        return apps

    async def _save_to_disk(self, apps: List[Dict]):
        def save():
            with open(APP_LIST_FILE, "w", encoding="utf-8") as f:
                json.dump({"applist": {"apps": apps}}, f)
        await asyncio.to_thread(save)

    def _tokenize(self, text: str) -> Set[str]:
        """Quebra texto em tokens normalizados para indexação."""
        # Apenas alfanuméricos lowercase
        return set(re.findall(r"\w+", text.lower()))

    def _build_index(self, apps: List[Dict]):
        """
        Cria um índice invertido simples: Token -> Set[AppIDs]
        E um mapa direto: AppID -> Nome
        """
        self._app_index = {}
        self._app_map = {}
        
        # Palavras ignoradas (stopwords comuns em nomes de jogos) para economizar RAM indexando
        stopwords = {"the", "a", "an", "of", "in", "on", "at", "to", "for", "by", "edition", "pack", "dlc"}

        for app in apps:
            appid = app["appid"]
            name = app["name"]
            
            if not name:
                continue
                
            self._app_map[appid] = name
            
            # Indexação
            tokens = self._tokenize(name)
            for token in tokens:
                # Ignorar tokens muito curtos (<3) EXCETO se for digito ou "io"/"go"
                if len(token) < 3 and not token.isdigit() and token not in ("io", "go"):
                    continue
                if token in stopwords:
                    continue
                    
                if token not in self._app_index:
                    self._app_index[token] = set()
                self._app_index[token].add(appid)

    # =========================================================================
    #  FUZZY SEARCH ENGINE
    # =========================================================================

    def _local_search(self, query: str) -> Optional[int]:
        """
        Realiza busca fuzzy no índice local.
        Retorna o AppID com melhor match ou None.
        """
        if not self._app_list_loaded:
            return None
            
        clean_query = self.sanitize_search_term(query).lower()
        if not clean_query:
            return None
            
        tokens = self._tokenize(clean_query)
        if not tokens:
            return None

        # 1. Encontrar candidatos (Interseção de tokens é muito restritiva, vamos usar União ponderada)
        # Se o jogo tem "God" e "War", ele aparece na lista de candidatos.
        # Jogos que tem MAIS tokens da query ganham prioridade.
        
        candidates: Dict[int, int] = {} # AppID -> Count de tokens matched
        
        for token in tokens:
            if token in self._app_index:
                for appid in self._app_index[token]:
                    candidates[appid] = candidates.get(appid, 0) + 1
        
        # Filtrar candidatos que tenham pelo menos 50% dos tokens (ou todos se for curto)
        min_matches = max(1, len(tokens) // 2)
        top_candidates = [aid for aid, count in candidates.items() if count >= min_matches]
        
        if not top_candidates:
            # Fallback: Tentar apenas o primeiro token (palavra chave principal)
            first_token = list(tokens)[0]
            if first_token in self._app_index:
                top_candidates = list(self._app_index[first_token])
        
        if not top_candidates:
            return None
            
        # Ordenar candidatos por número de matches (descendente) para não cortar os melhores
        # Isso é CRUCIAL pois tokens comuns ("2", "simulator") geram milhares de candidatos
        top_candidates.sort(key=lambda aid: candidates.get(aid, 0), reverse=True)

        # Limitar candidatos para o SequenceMatcher (é lento se tiver 10000)
        # Pegamos os top 100 mais frequentes se tiver muita coisa
        if len(top_candidates) > 500:
            top_candidates = top_candidates[:500]

        # 2. Ranking preciso com difflib (Jaro-Winkler like)
        best_ratio = 0.0
        best_id = None
        
        # Para otimizar, pré-calculamos o clean_query
        
        for appid in top_candidates:
            original_name = self._app_map.get(appid, "")
            # Limpar o nome do candidato também para comparação justa
            clean_original = self.sanitize_search_term(original_name).lower()
            
            # Comparação
            ratio = difflib.SequenceMatcher(None, clean_query, clean_original).ratio()
            
            # Boost para match exato contido (ex: "Terraria" busca em "Terraria")
            if clean_query == clean_original:
                ratio += 0.2
            
            # Boost para match exato contido (ex: "Terraria" busca em "Terraria")
            if clean_query == clean_original:
                ratio += 0.2
            
            # REMOVED: Substring Match Boost which was causing False Positives
            # e.g. "Yao-Guai Hunter" matches "Hunter" (0.95) -> WRONG
            # Now relying purely on Ratio + Sanitization.

            if ratio > best_ratio:
                best_ratio = ratio
                best_id = appid
        
        print(f"[SteamService Debug] '{query}' -> Melhor match: '{self._app_map.get(best_id)}' (Score: {best_ratio:.2f})")
        
        # Aceitar matches acima de 0.85 (fuzzy rigoroso para evitar falso positivo)
        # Se for menor, melhor falhar e tentar Fallback (SteamGridDB) ou Split Query
        if best_ratio > 0.85:
            return best_id
            
        return None

    # =========================================================================
    #  CORE SERVICE
    # =========================================================================

    def _get_from_cache(self, key: str) -> Optional[Dict]:
        if key in self._cache:
            item = self._cache[key]
            if time.time() < item["expires"]:
                return item["data"]
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, data: Any):
        self._cache[key] = {
            "data": data,
            "expires": time.time() + self._cache_ttl
        }

    def sanitize_search_term(self, query: str) -> str:
        """
        V6 Logic + Normalização
        """
        # 0. Normalização prévia
        s = query
        replacements = {
            "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."
        }
        for k, v in replacements.items():
            s = s.replace(k, v)

        # 1. Decodificar URL
        from urllib.parse import unquote
        s = unquote(s)
        
        # 2. Remover conteúdo entre colchetes/parenteses de forma segura
        # Removemos apenas se estiver no final ou for típico de repack
        s = re.sub(r"\[.*?\]", " ", s) # [FitGirl Repack]
        s = re.sub(r"\(.*?\)", " ", s) # (Build 123)
        s = re.sub(r"\{.*?\}", " ", s)

        # 3. Remover versões e builds
        # Match v1.0.2, 1.0.2 (must have dot for no-v), v1 (must have v for no-dot)
        s = re.sub(r"(?i)\bv\d[\w\.\-\+]*\b", " ", s)
        s = re.sub(r"(?i)\b\d+\.\d+[\w\.\-\+]*\b", " ", s)
        s = re.sub(r"(?i)\bbuild\s*\d+\b", " ", s)
        s = re.sub(r"(?i)\bversion\s*\d+\b", " ", s) # FIX: Catch 'Version 42'
        s = re.sub(r"(?i)\bupdate\s*\d+\b", " ", s)
        
        # Tags especificas de Scene/Release
        s = re.sub(r"(?i)\b(denuvoless|repack|cracked|portable|bonus)\b", " ", s)

        # 4. Substituir separadores por espaços
        # Inclui: . _ - + / \ : , ; > < [ ] { }
        s = re.sub(r"[._\-\+/\\:,;><\[\]\{\}]", " ", s) 
        
        # 5. Tags
        # Separate tags that usually have a quantity prefix (e.g. "5 DLCs")
        quantity_tags = [
            "dlc", "dlcs", "bonus", "bonuses", "ost", "soundtrack", "content", "supporter", "rewards",
            "emulator", "emulators", "switch", "yuzu", "ryujinx", "citra", "cemu", "build", "update"
        ]
        
        # General tags to remove (but NOT the number before them)
        # Removed "game" from this list as it kills "Game Tycoon" -> "Tycoon"
        general_tags = [
            "repack", "fitgirl", "dodi", "elamigos", "goldberg", "crack", "cracked",
            "skidrow", "codex", "plaza", "iso", "portable", "full", "pc",
            "edition", "goty", "complete", "remastered", "remake", 
            "bundle", "collection", "anthology", "trilogy", "quadrology", "saga",
            "digital", "deluxe", "ultimate", "gold", "silver", "platinum", "premium",
            "definitive", "director's", "directors", "cut", "expanded", "extended", "enhanced",
            "season", "pass"
        ]
        
        # Remove "Number + Quantity Tag" (e.g. "5 DLCs")
        q_pattern = "|".join(quantity_tags)
        s = re.sub(r"(?i)\b\d+\s+(" + q_pattern + r")\b", " ", s)
        
        # Remove just the tags (both types)
        all_tags = quantity_tags + general_tags
        all_pattern = "|".join(all_tags)
        s = re.sub(r"(?i)\b(" + all_pattern + r")\b", " ", s)
        
        # 6. Cleanup final
        s = re.sub(r"[^a-zA-Z0-9\s']", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        
        return s

    async def search_monitor(self, query: str) -> Optional[int]:
        """
        Busca AppID híbrida: Local (AppList) -> API (Fallback)
        """
        if not query:
            return None
        
        query_str = str(query).strip()
        if query_str.isdigit():
            return int(query_str)
        
        # 0. Cache check antes de tudo
        clean_query = self.sanitize_search_term(query_str)
        cache_key = f"search:{clean_query.lower()}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        # 1. TENTATIVA LOCAL (Rápida e Inteligente)
        # Garante carregamento do DB
        if not self._app_list_loaded:
            print("[SteamService] Inicializando busca local...")
            # Não fazemos await ensure_app_list() aqui para não travar a primeira request HTTP
            # disparamos em background se necessário, ou assumimos que startup fez
            await self.ensure_app_list()
        
        local_id = self._local_search(query_str) # Tenta com string original levemente limpa
        if not local_id and clean_query != query_str:
            local_id = self._local_search(clean_query) # Tenta com string sanitizada v6

        if local_id:
            print(f"[SteamService] [LOCAL] Encontrado: {local_id} ('{self._app_map[local_id]}') para '{query_str}'")
            self._set_cache(cache_key, local_id)
            return local_id

        # 2. FALLBACK API (Lenta e Estrita)
        print(f"[SteamService] [API] Local falhou. Tentando Store Search para '{clean_query}'")
        
        async with self._semaphore:
            client = await self._get_client()
            async def do_api_search(term):
                try:
                    url = "https://store.steampowered.com/api/storesearch/"
                    params = { "term": term, "l": "english", "cc": "US" }
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("total") > 0 and data.get("items"):
                            return int(data["items"][0]["id"])
                except Exception as e:
                    print(f"[SteamService] Erro API: {e}")
                return None
            
            api_id = await do_api_search(clean_query)
            
            # Retry API com menos palavras
            if not api_id and " " in clean_query:
                words = clean_query.split()
                if len(words) > 1:
                    short_q = " ".join(words[:2])
                    print(f"[SteamService] [API] Retry curto: '{short_q}'")
                    await asyncio.sleep(0.2)
                    api_id = await do_api_search(short_q)
            
            if api_id:
                print(f"[SteamService] [API] Encontrado: {api_id}")
                self._set_cache(cache_key, api_id)
                return api_id
        
        print(f"[SteamService] Nenhum resultado para '{clean_query}'")
        return None

    async def _validate_image(self, url: str) -> bool:
        try:
            # Validar se a imagem existe (HEAD request)
            # Timeout curto para não atrasar muito
            client = await self._get_client()
            resp = await client.head(url, timeout=1.5)
            return resp.status_code == 200
        except:
            return False

    async def get_game_details(self, app_id: int) -> Dict[str, Any]:
        """
        Busca detalhes completos do jogo na Steam API
        Retorna: descrição, gêneros, desenvolvedora, vídeos, etc
        """
        cache_key = f"details:{app_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            client = await self._get_client()
            url = f"https://store.steampowered.com/api/appdetails"
            params = {"appids": app_id, "l": "english"}
            
            resp = await client.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if str(app_id) in data and data[str(app_id)].get("success"):
                    app_data = data[str(app_id)]["data"]
                    
                    # Extrair vídeos
                    videos = []
                    if "movies" in app_data:
                        for movie in app_data["movies"][:3]:  # Primeiros 3 vídeos
                            if "webm" in movie:
                                videos.append({
                                    "name": movie.get("name", "Trailer"),
                                    "thumbnail": movie.get("thumbnail", ""),
                                    "webm": movie["webm"].get("480", ""),
                                    "mp4": movie.get("mp4", {}).get("480", "")
                                })
                    
                    # Extrair informações principais
                    details = {
                        "app_id": app_id,
                        "name": app_data.get("name", ""),
                        "description": app_data.get("short_description", ""),
                        "full_description": app_data.get("detailed_description", "")[:500],  # Primeiros 500 chars
                        "developers": app_data.get("developers", []),
                        "publishers": app_data.get("publishers", []),
                        "genres": [g.get("description", "") for g in app_data.get("genres", [])],
                        "categories": [c.get("description", "") for c in app_data.get("categories", [])],
                        "release_date": app_data.get("release_date", {}).get("date", ""),
                        "price": app_data.get("price_overview", {}).get("final_formatted", "Free"),
                        "metacritic": app_data.get("metacritic", {}).get("score", None),
                        "videos": videos,
                        "website": app_data.get("website", "")
                    }
                    
                    # Cachear por 24h
                    self._set_cache(cache_key, details)
                    return details
        except Exception as e:
            print(f"[SteamService] Erro ao buscar detalhes: {e}")
        
        return {}

    async def get_game_art(self, query: str) -> Dict[str, Optional[str]]:
        # Estratégia de "Split Retry": Tentar query original, e se falhar, tentar prefixo (antes de : ou -)
        # Isso resolve casos como "Game: DLC Bundle" ou "Game - Deluxe Edition"
        queries_to_try = [query]
        
        # Detectar separadores comuns de titulos compostos
        # Regex para separar em qualquer um destes: " – ", ": ", " - ", " — "
        # Pega o primeiro grupo (titulo base)
        import re
        match = re.split(r"(?:\s[–\-—]\s|:\s)", query, maxsplit=1)
        if match and len(match) > 1:
             base_title = match[0].strip()
             if len(base_title) > 3 and base_title not in queries_to_try:
                  queries_to_try.append(base_title)
        
        final_result = {
            "app_id": None,
            "header": None, "capsule": None, "hero": None, "logo": None, "background": None
        }

        for q in queries_to_try:
            print(f"[SteamService] Buscando arte para: '{q}'")
            app_id = await self.search_monitor(q)
            
            # Se achou app_id, monta o resultado e valida
            if app_id:
                base_cdn = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{app_id}"
                result = {
                    "app_id": app_id,
                    "header": f"{base_cdn}/header.jpg",
                    "capsule": f"{base_cdn}/capsule_616x353.jpg",
                    "hero": f"{base_cdn}/library_hero.jpg",
                    "logo": f"{base_cdn}/logo.png",
                    "background": f"{base_cdn}/page_bg_generated_v6b.jpg"
                }

                # VALIDAÇÃO DE IMAGEM (Anti-Soundtrack/DLC sem arte)
                # Verifica se o header existe. Se não existir, ignora esse AppID.
                is_valid = await self._validate_image(result["header"])
                
                if is_valid:
                    # Cachear com a query ORIGINAL também para agilizar futuro
                    cache_key = f"art:{app_id}"
                    self._set_cache(cache_key, result)
                    return result
                else:
                    print(f"[SteamService] ALERTA: AppID {app_id} encontrado mas sem 'header.jpg' (Provável Soundtrack/DLC). Ignorando.")
            
            # Se não achou na Steam (ou imagem falhou), e temos SGDB, tentamos SGDB para este Q
            if self.sgdb:
                 print(f"[SteamService] Fallback SteamGridDB para: '{q}'")
                 fallback_art = await self.sgdb.search_and_get_art(q)
                 if fallback_art:
                    final_result.update(fallback_art)
                    # Salvar cache da query original (não do Q) para resolver o request
                    fallback_key = f"art:fallback:{self.sanitize_search_term(query)}" 
                    self._set_cache(fallback_key, final_result)
                    return final_result

        return final_result

        cache_key = f"art:{app_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        base_cdn = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{app_id}"
        
        # Assumimos sucesso se temos AppID (CDN da Steam é padronizada)
        result = {
            "app_id": app_id,
            "header": f"{base_cdn}/header.jpg",
            "capsule": f"{base_cdn}/capsule_616x353.jpg",
            "hero": f"{base_cdn}/library_hero.jpg",
            "logo": f"{base_cdn}/logo.png",
            "background": f"{base_cdn}/page_bg_generated_v6b.jpg"
        }
        
        self._set_cache(cache_key, result)
        return result

# Instância global
steam_client = SteamClient()
