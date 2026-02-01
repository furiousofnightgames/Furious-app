"""
Resolver de Imagens de Jogos - Fallback Chain Completo
Implementa a estratégia de resolução 100% conforme plano_completo_imagens.md
"""

import re
from typing import Dict, Optional, Any
from datetime import datetime
from sqlmodel import select
from backend.steam_service import steam_client
from backend.db import get_session
from backend.models.models import ResolverAlias, SteamApp

# ============================================================================
# UTILS DE BUSCA E ARTE (Definidas no topo para visibilidade global)
# ============================================================================

async def _get_art_payload(game_name: str, app_id: int, priority: bool = False) -> Dict[str, Any]:
    """Helper para buscar arte e garantir formato de retorno padronizado"""
    art = await _fetch_game_art(app_id, game_name, priority=priority)
    if art.get("found"):
        return art
    return {"found": False, "appId": app_id, "error": "no_art"}


async def _fetch_game_art(app_id: int, game_name: str = None, priority: bool = False) -> Dict[str, Any]:
    """Busca arte de um AppID especifico, com fallback para SteamGridDB"""
    result = await steam_client.get_game_art(str(app_id), priority=priority)
    if result.get("app_id") and (result.get("header") or result.get("capsule") or result.get("hero")):
        return {"found": True, "appId": result.get("app_id"), **result}
    
    # Se nao encontrou arte no Steam, tenta SteamGridDB
    if game_name and steam_client.sgdb:
        steam_client._log(f"[Resolver] Nenhuma arte no Steam para AppID {app_id}, tentando SteamGridDB...")
        sgdb_result = await steam_client.sgdb.search_and_get_art(game_name)
        if sgdb_result:
            steam_client._log(f"[Resolver] Encontrado via SteamGridDB (fallback)")
            return {
                "found": True,
                "appId": None,
                "capsule": sgdb_result.get("capsule"),
                "header": sgdb_result.get("header"),
                "background": sgdb_result.get("background"),
                "grid": sgdb_result.get("grid"),
                "hero": sgdb_result.get("hero"),
                "logo": sgdb_result.get("logo")
            }
    
    return {"found": False, "error": "no_art"}



_resolver_telemetry: Dict[str, int] = {
    "cache_hit": 0,
    "rule_hit": 0,
    "steam_hit": 0,
    "sgdb_hit": 0,
    "reject_low_plausibility": 0,
    "sgdb_reject_low_plausibility": 0,
}


def _telemetry_inc(key: str, n: int = 1) -> None:
    try:
        _resolver_telemetry[key] = int(_resolver_telemetry.get(key, 0)) + int(n)
    except Exception:
        pass


def get_resolver_telemetry() -> Dict[str, int]:
    try:
        return dict(_resolver_telemetry)
    except Exception:
        return {}


def _get_db_alias_app_id(key: Optional[str]) -> Optional[int]:
    if not key:
        return None
    try:
        session = get_session()
        try:
            k = str(key).strip().lower()
            obj = session.exec(select(ResolverAlias).where(ResolverAlias.key == k)).first()
            if not obj:
                return None
            return int(obj.app_id)
        finally:
            session.close()
    except Exception:
        return None


async def _upsert_db_alias(key: Optional[str], app_id: Optional[int], force: bool = False) -> None:
    if not key or not app_id:
        return
    try:
        k = str(key).strip().lower()
        if not _is_safe_cache_key(k):
            steam_client._log(f"[Resolver] Alias ignorado (unsafe key): '{k}'")
            return
        
        # CRITICAL: Validate that the AppID actually matches the key before caching
        # But allow bypass for manual overrides or synthetic IDs
        if not force and not await _is_appid_match_plausible(k, int(app_id)):
            steam_client._log(f"[Resolver] BLOCKED bad alias: '{k}' -> {app_id} (plausibility check failed)")
            return
        
        steam_client._log(f"[Resolver] Tentando salvar alias: '{k}' -> {app_id} (Force={force})")
        session = get_session()
        try:
            existing = session.exec(select(ResolverAlias).where(ResolverAlias.key == k)).first()
            if existing:
                existing.app_id = int(app_id)
                existing.updated_at = datetime.now()
                session.add(existing)
                steam_client._log(f"[Resolver] Alias ATUALIZADO: '{k}' -> {app_id}")
            else:
                obj = ResolverAlias(key=k, app_id=int(app_id), created_at=datetime.now(), updated_at=datetime.now())
                session.add(obj)
                steam_client._log(f"[Resolver] Alias CRIADO: '{k}' -> {app_id}")
            session.commit()
        except Exception as e:
            steam_client._log(f"[Resolver] ERRO DB ao salvar alias '{k}': {e}")
        finally:
            session.close()
    except Exception as e_outer:
        print(f"[Resolver] CRITICAL ERROR in _upsert_db_alias: {e_outer}")


_GENERIC_CACHE_TOKENS = {
    "bonus", "bonuses", "dlc", "dlcs", "windows", "fix", "update", "version", "build",
    "bundle", "edition", "ultimate", "complete", "deluxe", "pack", "content",
}


def _is_generic_term(term: str) -> bool:
    if not term:
        return True
    sanitized = (steam_client.sanitize_search_term(str(term)) or "").strip().lower()
    if not sanitized:
        return True
    alpha_tokens = [t.lower() for t in re.findall(r"[a-zA-Z]+", sanitized) if t]
    if not alpha_tokens:
        return True
    return all(t in _GENERIC_CACHE_TOKENS for t in alpha_tokens)


def _is_safe_cache_key(key: str) -> bool:
    if not key:
        return False
    s = key.strip().lower()
    if len(s) < 2:
        return False
    if not re.search(r"[a-zA-Z]", s):
        return False
    parts = [p for p in re.findall(r"\w+", s.lower()) if p]
    if not parts:
        return False
    if all(p in _GENERIC_CACHE_TOKENS for p in parts):
        return False
    return True


def _make_session_cache_key(raw_name: str, normalized_name: str) -> Optional[str]:
    raw = (raw_name or "").strip()
    if not raw:
        return None

    # Removed aggressive splitting to preserve subtitles (e.g. "Hollow Knight: Silksong")
    key = steam_client.sanitize_search_term(raw) or (normalized_name or "")
    key = (key or "").strip().lower()
    return key if _is_safe_cache_key(key) else None


async def _is_appid_match_plausible(query: str, app_id: int) -> bool:
    """Delegate to central steam_client implementation (Async)"""
    return await steam_client.is_appid_match_plausible_async(query, app_id)


def _is_name_match_plausible(query: str, candidate_name: str) -> bool:
    """Delegate to central implementation"""
    return steam_client.is_name_match_plausible(query, candidate_name)


# ============================================================================
# REGRAS AUTOMÁTICAS - Mapeamento de abreviações comuns
# ============================================================================

AUTOMATIC_RULES = {
    # GTA Series - Specific mappings to prevent confusion
    "gta v": "Grand Theft Auto V",
    "gta 5": "Grand Theft Auto V",
    "gta vi": "Grand Theft Auto VI",
    "gta 6": "Grand Theft Auto VI",
    "gta iv": "Grand Theft Auto IV",
    "gta 4": "Grand Theft Auto IV",
    "gta iii": "Grand Theft Auto III",
    "gta 3": "Grand Theft Auto III",
    "gta vice city": "Grand Theft Auto Vice City",
    "gta san andreas": "Grand Theft Auto San Andreas",
    "gta ii": "Grand Theft Auto 2",
    "gta 2": "Grand Theft Auto 2",
    
    # Other games
    "lords of the fallen 2023": "Lords of the Fallen",
    "the lords of the fallen 2023": "Lords of the Fallen",
    "blood refreshed supply": "Blood: Fresh Supply",
    "blood: refreshed supply": "Blood: Fresh Supply",
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
# NORMALIZAÇÃO INTELIGENTE (Migrada para steam_service.py)
# ============================================================================


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


def _delete_cached_app_id(normalized_name: str):
    try:
        if normalized_name in _session_cache:
            del _session_cache[normalized_name]
    except Exception:
        pass


def clear_session_cache():
    """Limpa o cache de sessão completamente"""
    _session_cache.clear()
    steam_client._log("[Resolver] Cache de sessão limpo", force=True)


def _build_name_candidates(raw_name: str, normalized_name: str) -> list[str]:
    out: list[str] = []
    raw = (raw_name or "").strip()
    if not raw:
        return out

    # Prefer right side of slashed titles (e.g. "PT title / EN title").
    # IMPORTANT: do NOT split on slashes used as tag separators like "DLCs/Bonuses".
    # Only treat it as a bilingual title when it uses the spaced pattern " / ".
    if " / " in raw:
        parts = [p.strip() for p in raw.split(" / ") if p and p.strip()]
        if len(parts) >= 2:
            right = parts[-1]
            out.append(right)
            right_clean = steam_client.sanitize_search_term(right)
            if right_clean:
                out.append(right_clean)

    clean = steam_client.sanitize_search_term(raw)
    if clean:
        out.append(clean)

    # Try base title before ':' as a fallback candidate, but after the full title.
    # This prevents overly-generic prefixes like "Blood" from winning too early.
    if ":" in raw:
        left = raw.split(":", 1)[0].strip()
        if left:
            out.append(left)
            left_clean = steam_client.sanitize_search_term(left)
            if left_clean:
                out.append(left_clean)

    if normalized_name:
        out.append(normalized_name)

    words = clean.split() if clean else []
    if len(words) >= 2:
        out.append(" ".join(words[:2]))
    if words:
        out.append(words[0])

    seen = set()
    uniq: list[str] = []
    for s in out:
        key = (s or "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            if not _is_generic_term(s):
                uniq.append(s)
    return uniq




# ============================================================================
# FALLBACK CHAIN COMPLETA
# ============================================================================

async def resolve_game_images(game_name: str, priority: bool = False) -> Dict[str, Any]:
    """
    Tenta resolver AppID e Artes (Header, Capsule, Hero, Logo, Background).
    Ordem: Cache -> Manual Overrides -> Regras -> Busca Exata -> Busca Normalizada -> LLM (future).
    
    Retorna:
    {
        "found": bool,
        "appId": int | None,
        "capsule": str | None,
        "header": str | null,
        "background": str | None,
        "grid": str | None,
        "description": str | None
    }
    """
    
    game_name = (game_name or "").strip()
    steam_client._log(f"\n[Resolver] Iniciando resolução para: '{game_name}'")
    
    if not game_name:
        return {"found": False, "error": "empty_name"}
    
    # Priority express lane: user clicked on details
    if priority:
        steam_client._log(f"[Resolver] PRIORITY LANE: '{game_name}'")
    
    normalized = steam_client.normalize_game_name(game_name)
    session_cache_key = _make_session_cache_key(game_name, normalized)
    candidates = _build_name_candidates(game_name, normalized)

    # ========== TENTATIVA 0: Overrides Hardcoded (Correções Críticas - PRIORIDADE MÁXIMA) ==========
    # Deve rodar ANTES do cache para corrigir entradas viciadas.
    LOW_CONFIDENCE_MATCHES = ["counter-strike", "half-life"]

    HARD_APP_OVERRIDES = {
        "escape from ever after": 1996390,
        "tennis elbow 4": 760640,
        "reus 2": 1875060,
        "megami tensei iii": 1413480, 
        "hin megami": 1413480,       
        "abracookingdabra": "Abra-Cooking-Dabra",
        "brokenlore unfollow": 2133830,
        "craftlings": 1771110,
        "vampiress eternal duet": 3660110,
        "morphos": 4076480,
        "summer in mara": 3646810,
        "space marine 2": 2183900,
        "section 13": 2111870,
        "yao guai hunter": 2432560,
        "temple of elemental evil": 3843520,
        "starrupture": 1631270,
        # GTA Fixes
        "grand theft auto ii": 12180,
        "grand theft auto 2": 12180,
        "gta 2": 12180,
        "gta ii": 12180,
        "grand theft auto iii": 12100,
        "grand theft auto 3": 12100,
        "gta 3": 12100,
        "gta iii": 12100,
        
        # GTA IV
        "grand theft auto iv": 12210,
        "gta iv": 12210,
        "gta 4": 12210,
        
        # GTA San Andreas
        "grand theft auto san andreas": 12120,
        "gta san andreas": 12120,

        # Manual User Overrides
        "the gold river project": 1253220,
        "gold river project": 1253220,
        "the gold river project 01.26.01.26b": 1253220,

        
        # GTA Vice City
        "grand theft auto vice city": 12110,
        "gta vice city": 12110,
        "vice city": 12110,

        # GTA 1 / Classics
        "grand theft auto gta": 12170, # Matches "Grand Theft Auto / GTA (v2022..."
        "grand theft auto the original trilogy": 12170, # Mapping classics pack to GTA 1
        
        # User Reported Fixes (Batch)
        "expeditions viking": 445190,
        "one sole purpose": "One Sole Purpose", # Force SGDB (Obscure/Delisted)
        "tales of berseria": 429660,
        "husk": "Husk", # Force SGDB (Avoids 'Prison of Husks')
        "skylar plux": 452540,
        "mx vs atv supercross": 282050,
        "blazblue central": 586140,
        "bayonetta 2": "Bayonetta 2", # WiiU/Switch usage (Force SGDB)
        
        # More User Reports
        "impact winter": 468000,
        "spirit of sanada": 595450,
        "samurai warriors spirit": 595450,
        "assetto corsa": 244210,
        
        # User Reported Fixes (Turn 2)
        "a knight's quest": 1001090, # Correct ID
        "10 dead doves": 1564540, # Was matching Counter-Strike (AppID 10)
        "3 minutes to midnight": 832500, # Was matching Soundtrack
        "70 seconds survival": 878470, # Was matching Half-Life
        # Metroid Fixes (Forcing 0 ensures we skip Steam AppID search and use SGDB with clean name)
        "metroid prime 4": 0,
        "metroid prime remastered": 0,
        "metroid dread": 0,
    }

    # NO_STORE logic moved to Fallback Area (Attempt 7) to prevent breaking valid searches.
    
    # Check by patterns (whole word match) for ultimate robustness
    target_app_id = None
    import re
    for pattern, aid in HARD_APP_OVERRIDES.items():
        # Use regex boundary for ALL patterns to prevent collisions like 'gta ii' in 'gta iii'
        # CHECK RAW NAME TOO: Essential for cases where normalization strips key words (e.g. "The")
        if re.search(rf"\b{re.escape(pattern)}\b", normalized) or \
           re.search(rf"\b{re.escape(pattern)}\b", str(game_name).lower()):
            target_app_id = aid
            break

    if target_app_id is not None:
        steam_client._log(f"[Resolver] HARD OVERRIDE DETECTED: '{game_name}' -> {target_app_id}")
        _telemetry_inc("rule_hit")
        
        # Override name if pattern suggested a cleaner one
        clean_search_name = str(game_name)
        if target_app_id == 0:
             # For 0, we use the original pattern text as the "clean" name for SGDB
             clean_search_name = pattern.title() if len(pattern) > 3 else str(game_name)
        
        # Se o override for uma STRING, é um nome alternativo para busca (SGDB etc)
        if isinstance(target_app_id, str):
            game_name = target_app_id
            target_app_id = await steam_client.search_monitor(target_app_id, priority=priority)
            clean_search_name = game_name # Use the string override as search term
        
        if isinstance(target_app_id, (int, str)) and target_app_id is not None:
            art = await _fetch_game_art(int(target_app_id) if str(target_app_id).isdigit() else 0, clean_search_name, priority=priority)
            
            if art.get("found"):
                if session_cache_key and str(target_app_id).isdigit():
                    _set_cached_app_id(session_cache_key, int(target_app_id))
                    await _upsert_db_alias(session_cache_key, int(target_app_id), force=True)
                return art
            else:
                # If a HARD OVERRIDE matched but failed to find art (even on SGDB),
                # we MUST stop here. Continuing would likely match a wrong game (e.g. GTA 2 -> GTA 3).
                steam_client._log(f"[Resolver] Hard override '{pattern}' matched but no art found. Aborting.")
                return {"found": False, "error": "override_art_not_found"}

    # ========== TENTATIVA 1: Cache de Sessão (Em memória) ==========
    if session_cache_key:
        cached_id = _session_cache.get(session_cache_key)
        if cached_id:
            steam_client._log(f"[Resolver] Cache de sessao hit: {game_name} -> {cached_id}")
            return await _get_art_payload(game_name, cached_id, priority=priority)

    # ========== TENTATIVA 1.5: Busca Local Rápida (165k AppList) ==========
    # Busca instantânea no banco injetado. Se encontrar aqui, nem tenta API Steam.
    local_appid = await steam_client.find_appid_locally(game_name)
    if not local_appid:
        # Tenta com o nome normalizado também antes de desistir do banco local
        local_appid = await steam_client.find_appid_locally(normalized)
    
    if local_appid:
        steam_client._log(f"[Resolver] AppID encontrado MANUALMENTE no banco local (AppList): {local_appid}")
        _telemetry_inc("steam_hit") # Conta como hit "oficial"
        art = await _fetch_game_art(local_appid, (candidates[0] if candidates else game_name), priority=priority)
        if art.get("found"):
            if session_cache_key:
                _set_cached_app_id(session_cache_key, local_appid)
                await _upsert_db_alias(session_cache_key, local_appid, force=True)
            return art

    # ========== TENTATIVA 2: Regras Automáticas ==========
    # NOTE: normalize_game_name strips parenthetical content like "(2023)",
    # but some franchises have ambiguous titles across years.
    # So we also try the session cache key (base title sanitization) as a rule key.
    rule_match = AUTOMATIC_RULES.get(normalized) or (AUTOMATIC_RULES.get(session_cache_key) if session_cache_key else None)
    if rule_match:
        _telemetry_inc("rule_hit")
        steam_client._log(f"[Resolver] Regra automatica: '{game_name}' -> '{rule_match}'")
        app_id = await steam_client.search_monitor(rule_match, priority=priority)
        if app_id and await _is_appid_match_plausible(rule_match, int(app_id)):
            art = await _fetch_game_art(app_id, rule_match, priority=priority)
            if art.get("found"):
                _telemetry_inc("steam_hit")
                if session_cache_key and art.get("appId"):
                    _set_cached_app_id(session_cache_key, int(art.get("appId")))
                    await _upsert_db_alias(session_cache_key, int(art.get("appId")), force=True)
                return art
    
    # ========== TENTATIVA 3: Busca Exata (nome original) ==========
    steam_client._log(f"[Resolver] Tentativa 3: Busca exata com nome original")
    matched_name = None
    for candidate in candidates:
        app_id = await steam_client.search_monitor(candidate, priority=priority)
        if not app_id:
            continue
        if not await _is_appid_match_plausible(candidate, int(app_id)):
            _telemetry_inc("reject_low_plausibility")
            steam_client._log(f"[Resolver] AppID rejeitado por baixa plausibilidade: {app_id}")
            continue
        matched_name = candidate
        steam_client._log(f"[Resolver] Encontrado via busca exata: {app_id}")

        art = await _fetch_game_art(app_id, matched_name or game_name, priority=priority)
        
        # HEURISTICA ANTI-DLC: Se o resultado for DLC/Música mas a busca não pediu, rejeita.
        res_type = str(art.get("type", "")).lower()
        if res_type in ["dlc", "music", "demo", "advertising"]:
            # Verifica se o termo de busca sugere explicitamente DLC
            search_intent_dlc = any(x in game_name.lower() for x in ["dlc", "soundtrack", "ost", "demo", "expansion", "pack", "bonus"])
            if not search_intent_dlc:
                steam_client._log(f"[Resolver] Rejeitado {app_id} ({res_type}) pois a busca '{game_name}' não parece específica.")
                continue

        if art.get("found"):
            _telemetry_inc("steam_hit")
            if session_cache_key and art.get("appId"):
                _set_cached_app_id(session_cache_key, int(art.get("appId")))
                await _upsert_db_alias(session_cache_key, int(art.get("appId")), force=True)
            return art
    
    # ========== TENTATIVA 4: Busca com Normalização ==========
    steam_client._log(f"[Resolver] Tentativa 4: Busca com normalizacao")
    if normalized != game_name and normalized:
        app_id = await steam_client.search_monitor(normalized, priority=priority)
        if app_id and await _is_appid_match_plausible(normalized, int(app_id)):
            steam_client._log(f"[Resolver] Encontrado via normalizacao: {app_id}")
            art = await _fetch_game_art(app_id, (candidates[0] if candidates else game_name), priority=priority)
            
            # HEURISTICA ANTI-DLC (Repetido para Tentativa 4)
            res_type = str(art.get("type", "")).lower()
            if res_type in ["dlc", "music", "demo", "advertising"]:
                search_intent_dlc = any(x in game_name.lower() for x in ["dlc", "soundtrack", "ost", "demo", "expansion", "pack", "bonus"])
                if not search_intent_dlc:
                    steam_client._log(f"[Resolver] Rejeitado {app_id} ({res_type}) via normalização.")
                    # Não podemos dar 'continue' aqui pois é if/else simples, entao apenas não retornamos
                elif art.get("found"):
                    _telemetry_inc("steam_hit")
                    if session_cache_key and art.get("appId"):
                        _set_cached_app_id(session_cache_key, int(art.get("appId")))
                        await _upsert_db_alias(session_cache_key, int(art.get("appId")), force=True)
                    return art
            elif art.get("found"): # Se não for DLC, retorna normal
                _telemetry_inc("steam_hit")
                if session_cache_key and art.get("appId"):
                    _set_cached_app_id(session_cache_key, int(art.get("appId")))
                    await _upsert_db_alias(session_cache_key, int(art.get("appId")), force=True)
                return art
        elif app_id:
            _telemetry_inc("reject_low_plausibility")
    
    # ========== TENTATIVA 5: Fuzzy Matching Local ==========
    steam_client._log(f"[Resolver] Tentativa 5: Fuzzy matching local")
    # O steam_client já faz fuzzy matching internamente, então aqui apenas
    # tentamos com a versão normalizada novamente se não foi tentada
    
    # ========== TENTATIVA 6: Fallback SteamGridDB ==========
    steam_client._log(f"[Resolver] Tentativa 6: Fallback SteamGridDB")
    if steam_client.sgdb:
        for candidate in candidates or [game_name]:
            steam_client._log(f"[Resolver] Tentando SteamGridDB para: '{candidate}'")
            sgdb_result = await steam_client.sgdb.search_and_get_art(candidate)
            if not sgdb_result:
                continue
            # If provider returns a name, validate match to reduce wrong images.
            sgdb_name = None
            if isinstance(sgdb_result, dict):
                sgdb_name = sgdb_result.get("name") or sgdb_result.get("game_name")
            if sgdb_name and not _is_name_match_plausible(candidate, sgdb_name):
                _telemetry_inc("sgdb_reject_low_plausibility")
                steam_client._log(f"[Resolver] SteamGridDB rejeitado por baixa plausibilidade: '{candidate}' -> '{sgdb_name}'")
                continue
            steam_client._log("[Resolver] Encontrado via SteamGridDB")
            _telemetry_inc("sgdb_hit")
            
            res_capsule = sgdb_result.get("capsule")
            res_header = sgdb_result.get("header")
            res_hero = sgdb_result.get("hero")
            
            # HYTALE/INDIE QUALITY BOOST: uses Hero as Capsule for cinematic look
            if "hytale" in normalized:
                # Forçamos o Hero no Hytale conforme pedido do user (é muito mais bonito)
                res_capsule = res_hero or res_header or res_capsule
            elif not res_capsule:
                res_capsule = res_hero or res_header

            # SYNTHETIC ID SYSTEM: Give this indie game a stable High-Range ID (> 500M)
            # This allows it to be saved in GameMetadata and show up in the Library Grid.
            synthetic_aid = steam_client.get_synthetic_id(sgdb_name or candidate)
            
            final_art = {
                "found": True,
                "appId": synthetic_aid,
                "capsule": res_capsule,
                "header": res_header,
                "background": sgdb_result.get("background"),
                "grid": sgdb_result.get("grid"),
                "hero": res_hero,
                "logo": sgdb_result.get("logo"),
                "game_name": sgdb_name or candidate
            }
            
            # Persist synthetic alias and metadata for library grid restoration
            await _upsert_db_alias(session_cache_key, synthetic_aid, force=True)
            steam_client.persist_metadata(final_art)

            return final_art
    
    # ========== TENTATIVA 7: Explicit Non-Steam Fallback ==========
    # ========== TENTATIVA 7: Explicit Non-Steam Fallback ==========
    EXPLICIT_NON_STEAM_GAMES = [
        "usac code breach", 
        "void marauders",
        "yao-guai hunter",
        "pathologic 3",
        "starrupture"
    ]
    
    # Specific fix for CROSAK: Force failure/no-image as requested by user
    if "crosak" in normalized:
         steam_client._log(f"[Resolver] CROSAK detectado - Forçando Sem Imagem (User Request)")
         return {"found": False, "error": "blacklisted_no_image"}

    for non_steam in EXPLICIT_NON_STEAM_GAMES:
        # Whole word match to avoid collision with "Starrupture 2" or "Pathologic 3000"
        if re.search(rf"\b{re.escape(non_steam)}\b", normalized):
            steam_client._log(f"[Resolver] Fallback para Jogo FORA DA LOJA: '{game_name}'")
            synthetic_aid = steam_client.get_synthetic_id(game_name)
            return {
                "found": True,
                "appId": synthetic_aid,
                "not_found_on_store": True,
                "capsule": "https://img.freepik.com/free-vector/video-game-concept-illustration_114360-1534.jpg", # Placeholder Premium
                "header": "https://img.freepik.com/free-vector/gradient-gaming-background_23-2149129402.jpg",
                "game_name": game_name,
                "genres": ["Custom Games"],
                "developer": "Community"
            }

    # ========== FALHA TOTAL ==========
    steam_client._log(f"[Resolver] Nenhuma imagem encontrada para: '{game_name}'")
    
    # CRITICAL: Persist negative result as metadata to break the optimization loop
    try:
        synthetic_aid = steam_client.get_synthetic_id(game_name)
        stub = {
            "appId": synthetic_aid,
            "name": game_name,
            "not_found_on_store": True,
            "found": False
        }
        steam_client.persist_metadata(stub)
        # Also save as alias if possible to speed up next check
        if session_cache_key:
             import asyncio
             asyncio.create_task(_upsert_db_alias(session_cache_key, synthetic_aid, force=True))
    except Exception:
        pass

    return {"found": False, "error": "not_found", "appId": (synthetic_aid if 'synthetic_aid' in locals() else None)}

