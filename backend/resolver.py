"""
Resolver de Imagens de Jogos - Fallback Chain Completo
Implementa a estratégia de resolução 100% conforme plano_completo_imagens.md
"""

import re
from typing import Dict, Optional, Any
from backend.steam_service import steam_client


# ============================================================================
# REGRAS AUTOMÁTICAS - Mapeamento de abreviações comuns
# ============================================================================

AUTOMATIC_RULES = {
    # Formato: "entrada_normalizada" -> "nome_oficial_steam"
    "gta v": "Grand Theft Auto V",
    "gta 5": "Grand Theft Auto V",
    "gta vi": "Grand Theft Auto VI",
    "gta 6": "Grand Theft Auto VI",
    "cod mw3": "Call of Duty Modern Warfare III",
    "cod mw2": "Call of Duty Modern Warfare II",
    "cod mw": "Call of Duty Modern Warfare",
    "cod bo6": "Call of Duty Black Ops 6",
    "cod bo5": "Call of Duty Black Ops Cold War",
    "ac2": "Assassin's Creed II",
    "ac3": "Assassin's Creed III",
    "ac4": "Assassin's Creed IV Black Flag",
    "ac origins": "Assassin's Creed Origins",
    "ac odyssey": "Assassin's Creed Odyssey",
    "ac valhalla": "Assassin's Creed Valhalla",
    "spiderman": "Marvel's Spider-Man",
    "spider man": "Marvel's Spider-Man",
    "elden ring": "ELDEN RING",
    "dark souls 1": "Dark Souls",
    "dark souls 2": "Dark Souls II",
    "dark souls 3": "Dark Souls III",
    "ds1": "Dark Souls",
    "ds2": "Dark Souls II",
    "ds3": "Dark Souls III",
    "ff7": "Final Fantasy VII",
    "ff8": "Final Fantasy VIII",
    "ff10": "Final Fantasy X",
    "ff15": "Final Fantasy XV",
    "ff16": "Final Fantasy XVI",
    "rdr2": "Red Dead Redemption 2",
    "rdr": "Red Dead Redemption",
    "tlou": "The Last of Us",
    "tlou2": "The Last of Us Part II",
    "gta online": "Grand Theft Auto Online",
    "minecraft": "Minecraft",
    "fortnite": "Fortnite",
    "valorant": "VALORANT",
    "cs2": "Counter-Strike 2",
    "csgo": "Counter-Strike Global Offensive",
    "dota 2": "Dota 2",
    "lol": "League of Legends",
    "wow": "World of Warcraft",
    "ow2": "Overwatch 2",
    "halo infinite": "Halo Infinite",
    "starfield": "Starfield",
    "baldurs gate 3": "Baldur's Gate 3",
    "bg3": "Baldur's Gate 3",
    "cyberpunk 2077": "Cyberpunk 2077",
    "cp2077": "Cyberpunk 2077",
    "witcher 3": "The Witcher 3 Wild Hunt",
    "w3": "The Witcher 3 Wild Hunt",
    "skyrim": "The Elder Scrolls V Skyrim",
    "tes5": "The Elder Scrolls V Skyrim",
    "oblivion": "The Elder Scrolls IV Oblivion",
    "morrowind": "The Elder Scrolls III Morrowind",
    "fallout 4": "Fallout 4",
    "fallout 3": "Fallout 3",
    "fnv": "Fallout New Vegas",
    "fallout new vegas": "Fallout New Vegas",
    "terraria": "Terraria",
    "stardew valley": "Stardew Valley",
    "hollow knight": "Hollow Knight",
    "celeste": "Celeste",
    "hades": "Hades",
    "portal 2": "Portal 2",
    "half life 2": "Half-Life 2",
    "half life alyx": "Half-Life Alyx",
    "hl2": "Half-Life 2",
    "hla": "Half-Life Alyx",
}


# ============================================================================
# NORMALIZAÇÃO INTELIGENTE
# ============================================================================

def normalize_game_name(name: str) -> str:
    """
    Normaliza um nome de jogo para busca.
    Aplica:
    - lowercase
    - remover acentos
    - remover hífens/separadores
    - remover DLCs, versões, builds
    - limpar espaços excessivos
    """
    if not name:
        return ""
    
    s = str(name).strip()
    
    # 1. Normalizar caracteres especiais
    replacements = {
        "'": "'", "'": "'", """: '"', """: '"',
        "–": "-", "—": "-", "…": "..."
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    
    # 2. Decodificar URL
    from urllib.parse import unquote
    s = unquote(s)
    
    # 3. Remover conteúdo entre colchetes/parênteses (ANTES de separadores)
    s = re.sub(r"\[.*?\]", " ", s)  # [FitGirl Repack]
    s = re.sub(r"\(.*?\)", " ", s)  # (Build 123)
    s = re.sub(r"\{.*?\}", " ", s)
    
    # 4. Remover versões e builds (mais agressivo)
    s = re.sub(r"(?i)\bv\d[\w\.\-\+]*\b", " ", s)  # v1.0, v2.5.1, etc
    s = re.sub(r"(?i)\b\d+\.\d+[\w\.\-\+]*\b", " ", s)  # 1.0, 2.5.1, etc
    s = re.sub(r"(?i)\bbuild\s*\d+\b", " ", s)
    s = re.sub(r"(?i)\bversion\s*\d+\b", " ", s)
    s = re.sub(r"(?i)\bupdate\s*\d+\b", " ", s)
    s = re.sub(r"(?i)\brevision\s*\d+\b", " ", s)
    
    # 5. Remover tags de scene/release
    s = re.sub(r"(?i)\b(denuvoless|repack|cracked|portable|bonus|citron)\b", " ", s)
    
    # 6. Remover tags de emulador/plataforma
    s = re.sub(r"(?i)\b(switch|emulator|emulators|yuzu|ryujinx|citra|cemu)\b", " ", s)
    
    # 7. Substituir separadores por espaços (mantém estrutura)
    s = re.sub(r"[._\-\+/\\:,;><\[\]\{\}]", " ", s)
    
    # 8. Remover tags comuns (mais agressivo)
    quantity_tags = [
        "dlc", "dlcs", "bonus", "bonuses", "ost", "soundtrack", "content",
        "supporter", "rewards", "build", "update", "revision"
    ]
    
    general_tags = [
        "repack", "fitgirl", "dodi", "elamigos", "goldberg", "crack", "cracked",
        "skidrow", "codex", "plaza", "iso", "portable", "full", "pc",
        "edition", "goty", "complete", "remastered", "remake",
        "bundle", "collection", "anthology", "trilogy", "quadrology", "saga",
        "digital", "deluxe", "ultimate", "gold", "silver", "platinum", "premium",
        "definitive", "director's", "directors", "cut", "expanded", "extended",
        "enhanced", "season", "pass", "citron", "denuvoless"
    ]
    
    q_pattern = "|".join(quantity_tags)
    s = re.sub(r"(?i)\b\d+\s+(" + q_pattern + r")\b", " ", s)
    
    all_tags = quantity_tags + general_tags
    all_pattern = "|".join(all_tags)
    s = re.sub(r"(?i)\b(" + all_pattern + r")\b", " ", s)
    
    # 9. Cleanup final
    s = re.sub(r"[^a-zA-Z0-9\s']", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.lower()
    
    return s


# ============================================================================
# CACHE DE SESSÃO (nome → appId)
# ============================================================================

_session_cache: Dict[str, int] = {}


def _get_cached_app_id(normalized_name: str) -> Optional[int]:
    """Recupera AppID do cache de sessão"""
    return _session_cache.get(normalized_name)


def _set_cached_app_id(normalized_name: str, app_id: int):
    """Armazena AppID no cache de sessão"""
    _session_cache[normalized_name] = app_id


def clear_session_cache():
    """Limpa o cache de sessão completamente"""
    global _session_cache
    _session_cache.clear()
    print("[Resolver] Cache de sessão limpo")


# ============================================================================
# FALLBACK CHAIN COMPLETA
# ============================================================================

async def resolve_game_images(game_name: str) -> Dict[str, Any]:
    """
    Fallback chain completa para resolver imagens de um jogo.
    
    Retorna:
    {
        "found": bool,
        "appId": int | None,
        "capsule": str | None,
        "header": str | None,
        "background": str | None,
        "grid": str | None,
        "description": str | None
    }
    """
    
    if not game_name or not str(game_name).strip():
        return {"found": False, "error": "empty_name"}
    
    game_name = str(game_name).strip()
    try:
        print(f"\n[Resolver] Iniciando resolucao para: '{game_name}'")
    except:
        pass  # Ignore encoding errors in compiled exe
    
    # ========== TENTATIVA 1: Cache de Sessão ==========
    normalized = normalize_game_name(game_name)
    cached_app_id = _get_cached_app_id(normalized)
    if cached_app_id:
        # Evitar caracteres fora da codepage do console (problema no .exe)
        try:
            print(f"[Resolver] Cache hit: {cached_app_id}")
        except Exception:
            # Ignorar erros de encoding em ambientes restritos (PyInstaller/.exe)
            pass
        return await _fetch_game_art(cached_app_id, game_name)
    
    # ========== TENTATIVA 2: Regras Automáticas ==========
    rule_match = AUTOMATIC_RULES.get(normalized)
    if rule_match:
        try:
            print(f"[Resolver] Regra automatica: '{game_name}' -> '{rule_match}'")
        except:
            pass
        app_id = await steam_client.search_monitor(rule_match)
        if app_id:
            _set_cached_app_id(normalized, app_id)
            return await _fetch_game_art(app_id, game_name)
    
    # ========== TENTATIVA 3: Busca Exata (nome original) ==========
    try:
        print(f"[Resolver] Tentativa 3: Busca exata com nome original")
    except:
        pass
    app_id = await steam_client.search_monitor(game_name)
    if app_id:
        try:
            print(f"[Resolver] Encontrado via busca exata: {app_id}")
        except:
            pass
        _set_cached_app_id(normalized, app_id)
        return await _fetch_game_art(app_id, game_name)
    
    # ========== TENTATIVA 4: Busca com Normalização ==========
    try:
        print(f"[Resolver] Tentativa 4: Busca com normalizacao")
    except:
        pass
    if normalized != game_name:
        app_id = await steam_client.search_monitor(normalized)
        if app_id:
            try:
                print(f"[Resolver] Encontrado via normalizacao: {app_id}")
            except:
                pass
            _set_cached_app_id(normalized, app_id)
            return await _fetch_game_art(app_id, game_name)
    
    # ========== TENTATIVA 5: Fuzzy Matching Local ==========
    try:
        print(f"[Resolver] Tentativa 5: Fuzzy matching local")
    except:
        pass
    # O steam_client já faz fuzzy matching internamente, então aqui apenas
    # tentamos com a versão normalizada novamente se não foi tentada
    
    # ========== TENTATIVA 6: Fallback SteamGridDB ==========
    try:
        print(f"[Resolver] Tentativa 6: Fallback SteamGridDB")
    except:
        pass
    if steam_client.sgdb:
        try:
            print(f"[Resolver] Tentando SteamGridDB para: '{game_name}'")
        except:
            pass
        sgdb_result = await steam_client.sgdb.search_and_get_art(game_name)
        if sgdb_result:
            try:
                print(f"[Resolver] Encontrado via SteamGridDB")
            except:
                pass
            return {
                "found": True,
                "appId": None,  # SteamGridDB não tem appId
                "capsule": sgdb_result.get("capsule"),
                "header": sgdb_result.get("header"),
                "background": sgdb_result.get("background"),
                "grid": sgdb_result.get("grid"),
                "hero": sgdb_result.get("hero"),
                "logo": sgdb_result.get("logo")
            }
    
    # ========== FALHA TOTAL ==========
    try:
        print(f"[Resolver] Nenhuma imagem encontrada para: '{game_name}'")
    except:
        pass
    return {"found": False, "error": "not_found"}


async def _fetch_game_art(app_id: int, game_name: str = None) -> Dict[str, Any]:
    """Busca arte de um AppID especifico, com fallback para SteamGridDB"""
    result = await steam_client.get_game_art(str(app_id))
    if result.get("app_id") and (result.get("header") or result.get("capsule") or result.get("hero")):
        return {"found": True, **result}
    
    # Se nao encontrou arte no Steam, tenta SteamGridDB
    if game_name and steam_client.sgdb:
        try:
            print(f"[Resolver] Nenhuma arte no Steam para AppID {app_id}, tentando SteamGridDB...")
        except:
            pass
        sgdb_result = await steam_client.sgdb.search_and_get_art(game_name)
        if sgdb_result:
            try:
                print(f"[Resolver] Encontrado via SteamGridDB (fallback)")
            except:
                pass
            return {
                "found": True,
                "appId": app_id,
                "capsule": sgdb_result.get("capsule"),
                "header": sgdb_result.get("header"),
                "background": sgdb_result.get("background"),
                "grid": sgdb_result.get("grid"),
                "hero": sgdb_result.get("hero"),
                "logo": sgdb_result.get("logo")
            }
    
    return {"found": False, "error": "no_art"}
