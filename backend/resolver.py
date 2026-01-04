"""
Resolver de Imagens de Jogos - Fallback Chain Completo
Implementa a estratégia de resolução 100% conforme plano_completo_imagens.md
"""

import re
from typing import Dict, Optional, Any
from backend.steam_service import steam_client
from backend.db import get_session
from backend.models.models import ResolverAlias
from datetime import datetime
from sqlmodel import select


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


def _upsert_db_alias(key: Optional[str], app_id: Optional[int]) -> None:
    if not key or not app_id:
        return
    try:
        k = str(key).strip().lower()
        if not _is_safe_cache_key(k):
            return
        
        # CRITICAL: Validate that the AppID actually matches the key before caching
        # This prevents pollution like "GTA II" -> 3240220 (which is GTA V)
        if not _is_appid_match_plausible(k, int(app_id)):
            try:
                print(f"[Resolver] BLOCKED bad alias: '{k}' -> {app_id} (plausibility check failed)")
            except:
                pass
            return
        
        session = get_session()
        try:
            existing = session.exec(select(ResolverAlias).where(ResolverAlias.key == k)).first()
            if existing:
                existing.app_id = int(app_id)
                existing.updated_at = datetime.utcnow()
                session.add(existing)
            else:
                obj = ResolverAlias(key=k, app_id=int(app_id), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
                session.add(obj)
            session.commit()
        finally:
            session.close()
    except Exception:
        return


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
    if len(s) < 4:
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


def _roman_to_int(s: str) -> Optional[int]:
    if not s:
        return None
    t = s.strip().upper()
    if not re.fullmatch(r"[IVXLCDM]+", t):
        return None
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev = 0
    for ch in reversed(t):
        v = values.get(ch)
        if v is None:
            return None
        if v < prev:
            total -= v
        else:
            total += v
            prev = v
    return total if total > 0 else None


def _extract_numbers_and_roman(text: str) -> set[str]:
    if not text:
        return set()
    tokens = re.findall(r"\b\d+\b", text)
    romans = re.findall(r"\b[ivxlcdm]+\b", text)
    out = set()
    for t in tokens:
        # Ignore years like (2023) / (2014) that appear in release titles.
        # Steam names often omit the year, and treating it as a required number
        # causes false rejections.
        try:
            if len(t) == 4:
                y = int(t)
                if 1970 <= y <= 2099:
                    continue
        except Exception:
            pass
        out.add(t)
    for r in romans:
        out.add(r.lower())
    return out


def _tokenize(text: str) -> set[str]:
    if not text:
        return set()
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _is_appid_match_plausible(query: str, app_id: int) -> bool:
    """Reject obvious false positives (e.g. Battlefield 6 resolving to Battlefield V).

    Uses:
    - numeric/roman tokens compatibility
    - minimum token overlap (only when the query has enough signal)
    """
    try:
        cand_name = None
        if getattr(steam_client, "_app_map", None) and int(app_id) in steam_client._app_map:
            cand_name = steam_client._app_map.get(int(app_id))
        if not cand_name:
            return True

        q_norm = normalize_game_name(query)
        c_norm = normalize_game_name(cand_name)

        q_nums = _extract_numbers_and_roman(q_norm)
        c_nums = _extract_numbers_and_roman(c_norm)
        if q_nums and not q_nums.issubset(c_nums):
            return False

        q_tokens = _tokenize(q_norm)
        c_tokens = _tokenize(c_norm)
        stop = {"the", "a", "an", "of", "in", "on", "at", "to", "for", "by", "edition", "pack", "bundle", "complete"}
        q_sig = {t for t in q_tokens if t and t not in stop and len(t) >= 2}
        c_sig = {t for t in c_tokens if t and t not in stop and len(t) >= 2}

        if len(q_sig) >= 3:
            overlap = len(q_sig & c_sig)
            ratio = overlap / max(1, len(q_sig))
            if ratio < 0.55:
                return False
        return True
    except Exception:
        return True


def _is_name_match_plausible(query: str, candidate_name: str) -> bool:
    try:
        if not query or not candidate_name:
            return True
        q_norm = normalize_game_name(query)
        c_norm = normalize_game_name(candidate_name)

        q_nums = _extract_numbers_and_roman(q_norm)
        c_nums = _extract_numbers_and_roman(c_norm)
        if q_nums and not q_nums.issubset(c_nums):
            return False

        q_tokens = _tokenize(q_norm)
        c_tokens = _tokenize(c_norm)
        stop = {"the", "a", "an", "of", "in", "on", "at", "to", "for", "by", "edition", "pack", "bundle", "complete"}
        q_sig = {t for t in q_tokens if t and t not in stop and len(t) >= 2}
        c_sig = {t for t in c_tokens if t and t not in stop and len(t) >= 2}

        # If query is very short, don't over-filter.
        if len(q_sig) <= 2:
            return True

        overlap = len(q_sig & c_sig)
        ratio = overlap / max(1, len(q_sig))
        return ratio >= 0.55
    except Exception:
        return True


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


def _delete_cached_app_id(normalized_name: str):
    try:
        if normalized_name in _session_cache:
            del _session_cache[normalized_name]
    except Exception:
        pass


def clear_session_cache():
    """Limpa o cache de sessão completamente"""
    global _session_cache
    _session_cache.clear()
    print("[Resolver] Cache de sessão limpo")


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
    candidates = _build_name_candidates(game_name, normalized)

    session_cache_key = _make_session_cache_key(game_name, normalized)

    # ========== TENTATIVA 1.5: Alias persistido no SQLite (auto-aprendizado) ==========
    # Only for safe, non-generic keys.
    db_alias_app_id = _get_db_alias_app_id(session_cache_key)
    if db_alias_app_id:
        try:
            print(f"[Resolver] DB alias hit: {session_cache_key} -> {db_alias_app_id}")
        except Exception:
            pass
        art = await _fetch_game_art(db_alias_app_id, game_name)
        if art.get("found"):
            _telemetry_inc("steam_hit")
            if session_cache_key and art.get("appId"):
                _set_cached_app_id(session_cache_key, int(art.get("appId")))
            return art
    cached_app_id = _get_cached_app_id(session_cache_key) if session_cache_key else None
    if cached_app_id:
        _telemetry_inc("cache_hit")
        # Evitar caracteres fora da codepage do console (problema no .exe)
        try:
            print(f"[Resolver] Cache hit: {cached_app_id}")
        except Exception:
            # Ignorar erros de encoding em ambientes restritos (PyInstaller/.exe)
            pass
        cached_res = await _fetch_game_art(cached_app_id, game_name)
        if cached_res.get("found"):
            return cached_res
        # Cache inválido (ex.: DLC). Remover e continuar.
        if session_cache_key:
            _delete_cached_app_id(session_cache_key)
    
    # ========== TENTATIVA 2: Regras Automáticas ==========
    # NOTE: normalize_game_name strips parenthetical content like "(2023)",
    # but some franchises have ambiguous titles across years.
    # So we also try the session cache key (base title sanitization) as a rule key.
    rule_match = AUTOMATIC_RULES.get(normalized) or (AUTOMATIC_RULES.get(session_cache_key) if session_cache_key else None)
    if rule_match:
        _telemetry_inc("rule_hit")
        try:
            print(f"[Resolver] Regra automatica: '{game_name}' -> '{rule_match}'")
        except:
            pass
        app_id = await steam_client.search_monitor(rule_match)
        if app_id and _is_appid_match_plausible(rule_match, int(app_id)):
            art = await _fetch_game_art(app_id, rule_match)
            if art.get("found"):
                _telemetry_inc("steam_hit")
                if session_cache_key and art.get("appId"):
                    _set_cached_app_id(session_cache_key, int(art.get("appId")))
                    _upsert_db_alias(session_cache_key, int(art.get("appId")))
                return art
    
    # ========== TENTATIVA 3: Busca Exata (nome original) ==========
    try:
        print(f"[Resolver] Tentativa 3: Busca exata com nome original")
    except:
        pass
    matched_name = None
    for candidate in candidates:
        app_id = await steam_client.search_monitor(candidate)
        if not app_id:
            continue
        if not _is_appid_match_plausible(candidate, int(app_id)):
            _telemetry_inc("reject_low_plausibility")
            try:
                print(f"[Resolver] AppID rejeitado por baixa plausibilidade: {app_id}")
            except:
                pass
            continue
        matched_name = candidate
        try:
            print(f"[Resolver] Encontrado via busca exata: {app_id}")
        except:
            pass

        art = await _fetch_game_art(app_id, matched_name or game_name)
        if art.get("found"):
            _telemetry_inc("steam_hit")
            if session_cache_key and art.get("appId"):
                _set_cached_app_id(session_cache_key, int(art.get("appId")))
                _upsert_db_alias(session_cache_key, int(art.get("appId")))
            return art
    
    # ========== TENTATIVA 4: Busca com Normalização ==========
    try:
        print(f"[Resolver] Tentativa 4: Busca com normalizacao")
    except:
        pass
    if normalized != game_name and normalized:
        app_id = await steam_client.search_monitor(normalized)
        if app_id and _is_appid_match_plausible(normalized, int(app_id)):
            try:
                print(f"[Resolver] Encontrado via normalizacao: {app_id}")
            except:
                pass
            art = await _fetch_game_art(app_id, (candidates[0] if candidates else game_name))
            if art.get("found"):
                _telemetry_inc("steam_hit")
                if session_cache_key and art.get("appId"):
                    _set_cached_app_id(session_cache_key, int(art.get("appId")))
                    _upsert_db_alias(session_cache_key, int(art.get("appId")))
                return art
        elif app_id:
            _telemetry_inc("reject_low_plausibility")
    
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
        for candidate in candidates or [game_name]:
            try:
                print(f"[Resolver] Tentando SteamGridDB para: '{candidate}'")
            except:
                pass
            sgdb_result = await steam_client.sgdb.search_and_get_art(candidate)
            if not sgdb_result:
                continue
            # If provider returns a name, validate match to reduce wrong images.
            sgdb_name = None
            if isinstance(sgdb_result, dict):
                sgdb_name = sgdb_result.get("name") or sgdb_result.get("game_name")
            if sgdb_name and not _is_name_match_plausible(candidate, sgdb_name):
                _telemetry_inc("sgdb_reject_low_plausibility")
                try:
                    print(f"[Resolver] SteamGridDB rejeitado por baixa plausibilidade: '{candidate}' -> '{sgdb_name}'")
                except:
                    pass
                continue
            try:
                print("[Resolver] Encontrado via SteamGridDB")
            except:
                pass
            sgdb_result["found"] = True
            _telemetry_inc("sgdb_hit")
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
        return {"found": True, "appId": result.get("app_id"), **result}
    
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
                # IMPORTANT: do NOT keep the original app_id here.
                # When Steam has no art for this app_id (common for DLC/soundtracks),
                # returning it poisons frontend fallbacks (header.jpg) and caches.
                "appId": None,
                "capsule": sgdb_result.get("capsule"),
                "header": sgdb_result.get("header"),
                "background": sgdb_result.get("background"),
                "grid": sgdb_result.get("grid"),
                "hero": sgdb_result.get("hero"),
                "logo": sgdb_result.get("logo")
            }
    
    return {"found": False, "error": "no_art"}
