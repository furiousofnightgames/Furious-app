import re
from typing import List, Dict, Optional
from sqlmodel import Session, select
from backend.models.models import Item, Source

class ItemMatchingService:
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalizes a game name using the robust logic from SteamService.
        - Removes editions, tags, versions, repacks, etc.
        """
        if not name:
            return ""
            
        s = name
        
        # 0. Basic Replacements
        replacements = {
            "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."
        }
        for k, v in replacements.items():
            s = s.replace(k, v)

        # 1. Decode URL (if applicable, though usually names are clean)
        # s = unquote(s) 
        
        # 2. Remove Bracket Content safely
        s = re.sub(r"\[.*?\]", " ", s) # [FitGirl Repack]
        s = re.sub(r"\(.*?\)", " ", s) # (Build 123)
        s = re.sub(r"\{.*?\}", " ", s)

        # 3. Remove Versions and Builds
        s = re.sub(r"(?i)\bv\d[\w\.\-\+]*\b", " ", s)
        s = re.sub(r"(?i)\b\d+\.\d+[\w\.\-\+]*\b", " ", s)
        s = re.sub(r"(?i)\bbuild\s*\d+\b", " ", s)
        s = re.sub(r"(?i)\bversion\s*\d+\b", " ", s)
        s = re.sub(r"(?i)\bupdate\s*\d+\b", " ", s)
        
        # 4. Remove Specific Scene Tags
        s = re.sub(r"(?i)\b(denuvoless|repack|cracked|portable|bonus)\b", " ", s)

        # 5. Remove Separators
        s = re.sub(r"[._\-\+/\\:,;><\[\]\{\}]", " ", s) 
        
        # 6. Remove Quantity Tags and General Tags
        quantity_tags = [
            "dlc", "dlcs", "bonus", "bonuses", "ost", "soundtrack", "content", "supporter", "rewards",
            "emulator", "emulators", "switch", "yuzu", "ryujinx", "citra", "cemu", "build", "update"
        ]
        
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
        
        # 7. Final Cleanup (Alphanumeric only)
        s = re.sub(r"[^a-zA-Z0-9\s']", "", s)
        s = re.sub(r"\s+", " ", s).strip().lower()
        
        return s

    @staticmethod
    def find_equivalents(target_item: Item, candidates: List) -> List:
        """
        Finds equivalent items in a provided list of candidates.
        Returns a list of Items (or objects) that match the target item's name.
        """
        if not target_item or not target_item.name:
            return []
            
        target_norm = ItemMatchingService.normalize_name(target_item.name)
        if len(target_norm) < 3: # Too short to be reliable
            return []
            
        matches = []
        
        for item in candidates:
            # Skip the target item itself (if present in candidates)
            # Check by ID if available, or just ignore since we handled that in main.py loop
            # But let's be safe. Handle objects or dicts.
            i_id = getattr(item, 'id', None) or (item.get('id') if isinstance(item, dict) else None)
            i_source = getattr(item, 'source_id', None) or (item.get('source_id') if isinstance(item, dict) else None)
            
            t_id = getattr(target_item, 'id', None)
            t_source = getattr(target_item, 'source_id', None)
            
            if i_id and t_id and i_source and t_source:
                 if str(i_id) == str(t_id) and str(i_source) == str(t_source):
                     continue
            
            name = getattr(item, 'name', '') or (item.get('name') if isinstance(item, dict) else '')
            item_norm = ItemMatchingService.normalize_name(name)
            
            # Relaxed Match: Substring check
            # Handles cases like "Game v1.0" vs "Game"
            if item_norm and target_norm:
                 if item_norm == target_norm:
                     matches.append(item)
                     continue
                 # Bidirectional containment
                 # Ensure we don't match short common words by accident (len check at start helps)
                 if len(item_norm) > 4 and len(target_norm) > 4:
                     if item_norm in target_norm or target_norm in item_norm:
                         matches.append(item)
                         continue
            
        return matches

from backend.utils.tracker import UDPTrackerClient
import asyncio

class SourceHealthService:
    @staticmethod
    async def enrich_candidates(candidates: List) -> None:
        """
        Enriches a list of item candidates (dicts or objects) with real-time stats 
        from UDP trackers. Modifies the list in-place.
        """
        # Trackers extras sincronizados com engine/aria2_wrapper.py
        TRACKERS_EXTRAS = [
            "udp://tracker.opentrackr.org:1337/announce",
            "udp://open.stealth.si:80/announce",
            "udp://tracker.torrent.eu.org:451/announce",
            "udp://exodus.desync.com:6969/announce",
            "udp://tracker.moeking.me:6969/announce",
            "udp://tracker.openbittorrent.com:6969/announce",
            "udp://opentracker.i2p.rocks:6969/announce",
            "udp://tracker.internetwarriors.net:1337/announce",
            "udp://explodie.org:6969/announce",
            "udp://tracker.cyberia.is:6969/announce",
            "udp://tracker.birkenwald.de:6969/announce",
            "udp://tracker.tiny-vps.com:6969/announce",
            "udp://retracker.lanta-net.ru:2710/announce",
            "udp://ipv4.tracker.harry.lu:80/announce",
            "udp://tracker.theoks.net:6969/announce",
            "udp://tracker.ccp.ovh:6969/announce",
            "udp://bt1.archive.org:6969/announce",
            "udp://bt2.archive.org:6969/announce",
            "udp://tracker.filemail.com:6969/announce",
            "udp://tracker1.bt.moack.co.kr:80/announce",
            "udp://9.rarbg.com:2810/announce",
            "udp://tracker.uw0.xyz:6969/announce",
        ]

        client = UDPTrackerClient(timeout=1.5, retries=1)
        
        async def process_item(item):
            # Safe access to URL
            url = item.get('url') if isinstance(item, dict) else getattr(item, 'url', None)
            
            if not url or not url.startswith('magnet:'):
                return
            
            # Append extra trackers to maximize chances of finding seeds
            full_url = url
            for tr in TRACKERS_EXTRAS:
                full_url += f"&tr={tr}"
                
            stats = await client.get_stats(full_url)
            
            if stats:
                if isinstance(item, dict):
                    item['seeders'] = stats['seeders']
                    item['leechers'] = stats['leechers']
                    # Force recalc of score tag later or update it here?
                    # The main loop calls calculate_health_score AFTER this likely.
                else:
                    setattr(item, 'seeders', stats['seeders'])
                    setattr(item, 'leechers', stats['leechers'])

        # Process in parallel
        # Limit to avoid massive spam if list is huge, but usually candidates are few (<10)
        tasks = [process_item(c) for c in candidates[:10]]
        if tasks:
            await asyncio.gather(*tasks)

    @staticmethod
    def calculate_health_score(item: Item) -> Dict:
        """
        Calculates a health score based on Seeders/Leechers (if available/parsed).
        The Item model in this codebase might not have explicit 'seeders' column in DB 
        (checked models.py, it doesn't have 'seeders'). 
        
        Wait, Item in models.py (Step 122) DOES NOT have seeders.
        However, the JSON data often has it. 
        If the Item model doesn't store it, we can't sort by it unless we load it from the JSON 'extra' data or if it was added.
        
        Re-checking models.py from Step 122:
        Item has: id, source_id, name, url, size, category, type, image, icon, thumbnail, created_at.
        It misses 'seeders', 'peers'.
        
        However, in 'main.py' list_items loop (Step 131), we see:
        It loops raw items but returns a dict. It doesn't seem to persist seeders in DB Item table.
        
        CRITICAL: The Item table seems to be a cache of "known items" but mainly for 'Jobs' reference?
        Or is it populated from Sources?
        
        If 'Item' table does not have seeders, we might need to rely on the 'raw' data if we can get it,
        OR update the model.
        
        BUT, the requirement says "Preserve existing logic".
        
        Strategy:
        The `get_source_item` endpoint I added earlier and `list_items` return dictionaries with extra fields potentially?
        Let's look at `list_items` in `main.py` again.
        It returns a list of dicts. The dicts are built from `raw` JSON.
        They contain `seeders` if the JSON has it?
        Let's check `list_items` implementation in `main.py` (Step 131).
        It extracts: name, size, category, type, image, icon, thumbnail, uploadDate.
        IT DOES NOT EXPLICITLY EXTRACT SEEDERS in the snippet I saw!
        
        Wait, I need to check if `list_items` puts seeders in the dict.
        Line 1212 in Step 131:
        dict(id=..., name=..., url=..., size=..., category=..., type=..., source_id=..., image=..., icon=..., thumbnail=..., uploadDate=...)
        
        IT DOES NOT RETURN SEEDERS.
        
        This means Phase 1 also needs to ensure we extract/pass Seeders!
        
        Options:
        1. Modify `list_items` (and `Item` model?) to include seeders.
        2. Parse seeders in `find_equivalents` by re-reading the source JSON? That's heavy.
        
        The Plan says: "Métricas Coletadas por Fonte: Seeders ativos...".
        Functionality "Score " requires this.
        
        Correction: I should modify `main.py`'s `list_items` to extract seeders/peers from JSON data and pass it in the returned dicts.
        I don't necessarily need to save it to the DB if the DB is just a reference, but if `Item` is `table=True`, it's a DB table.
        
        If I change `list_items` to return raw seeders in the list (in-memory), I can use that for the analysis logic.
        But `find_equivalents` receives `Item` (DB objects) or `dict`?
        
        If `all_items` comes from `session.exec(select(Item))`, those are DB objects. They won't have seeders if the column doesn't exist.
        
        Hypothesis: The "Item" table only contains items that created Jobs? OR does it cache everything?
        `backend/main.py` logic:
        Line 886: `item = Item(...)` is created when creating a job.
        Line 1248: `delete(Item).where(Item.source_id == source_id)` implies items ARE stored per source?
        NO. `list_items` (endpoint) loads from JSON on demand!
        Line 1070: "Carrega items sob demanda da fonte (releitura do JSON)."
        
        So the DB `Item` table might NOT be the primary list of browsing items. The browsing happens via `list_items` which reads JSON.
        
        So, `find_equivalents` needs to:
        1. Iterate over all REGISTERED SOURCES in DB.
        2. For each source, LOAD its items (parse JSON).
        3. Search for matches.
        
        This is heavier but accurate to the current architecture (On-demand JSON).
        
        Matches User's "Heurística" requirement.
        
        So in `analysis.py`, I need `find_equivalents` to take `session` and iterate sources.
        
        """
        seeders = item.get('seeders', 0) if isinstance(item, dict) else getattr(item, 'seeders', 0)
        peers = item.get('leechers', 0) if isinstance(item, dict) else getattr(item, 'leechers', 0)
        
        # Safe cast to int
        try:
            seeders = int(seeders) if seeders is not None else 0
        except (ValueError, TypeError):
            seeders = 0
            
        try:
            peers = int(peers) if peers is not None else 0
        except (ValueError, TypeError):
            peers = 0
        
        # Check for Direct Download (HTTP/HTTPS) vs Magnet
        url = item.get('url') if isinstance(item, dict) else getattr(item, 'url', None)
        
        if url and not url.startswith('magnet:'):
            return {
                "score": 100,
                "label": "Direto",
                "color": "cyan",
                "seeders": None,
                "leechers": None,
                "is_direct": True
            }

        # Magnet Logic (Standard)
        if seeders >= 50:
            return {"score": 100, "label": "Excelente", "color": "emerald", "seeders": seeders, "leechers": peers}
        elif seeders >= 20:
            return {"score": 75, "label": "Bom", "color": "green", "seeders": seeders, "leechers": peers}
        elif seeders >= 5:
            return {"score": 50, "label": "Regular", "color": "yellow", "seeders": seeders, "leechers": peers}
        else:
            return {"score": 25, "label": f"Fraco ({seeders} seeds)", "color": "red", "seeders": seeders, "leechers": peers}
        # End of calculate_health_score

