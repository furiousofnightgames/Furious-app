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
            "season", "pass", "multiplayer", "online", "fix", "hotfix"
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
    def _tokenize(norm_name: str) -> set:
        if not norm_name:
            return set()
        # Common English/Gaming stopwords that dilute matching quality
        stopwords = {
            "the", "of", "and", "in", "at", "to", "for", "a", "an", "is", "by", 
            "edition", "version", "build", "v", "update", "dlc", "dlcs", "bonus"
        }
        tokens = set(norm_name.split())
        return tokens - stopwords

    @staticmethod
    def _jaccard_similarity(set1: set, set2: set) -> float:
        union = len(set1.union(set2))
        return len(set1.intersection(set2)) / union if union > 0 else 0.0

    @staticmethod
    def find_equivalents(target_item: Item, candidates: List) -> List:
        """
        Finds equivalent items using robust token-based similarity (Jaccard Index).
        Prevents false positives where items share only 1 common word (e.g. 'Multiplayer').
        """
        if not target_item or not target_item.name:
            return []
            
        target_norm = ItemMatchingService.normalize_name(target_item.name)
        if len(target_norm) < 3: 
            return []
            
        target_tokens = ItemMatchingService._tokenize(target_norm)
        matches = []
        
        for item in candidates:
            # Skip the target item itself
            i_id = getattr(item, 'id', None) or (item.get('id') if isinstance(item, dict) else None)
            i_source = getattr(item, 'source_id', None) or (item.get('source_id') if isinstance(item, dict) else None)
            
            t_id = getattr(target_item, 'id', None)
            t_source = getattr(target_item, 'source_id', None)
            
            if i_id and t_id and i_source and t_source:
                 if str(i_id) == str(t_id) and str(i_source) == str(t_source):
                     continue
            
            name = getattr(item, 'name', '') or (item.get('name') if isinstance(item, dict) else '')
            item_norm = ItemMatchingService.normalize_name(name)
            
            if not item_norm:
                continue

            # Exact match (Fast path)
            if item_norm == target_norm:
                matches.append(item)
                continue
                
            # Token Similarity (Robust path)
            item_tokens = ItemMatchingService._tokenize(item_norm)
            score = ItemMatchingService._jaccard_similarity(target_tokens, item_tokens)
            
            # Threshold: 
            # 0.5 is safer after removing stopwords.
            # "Lords of the Fallen" vs "Lords of Ravage" (Tokens: {lords, fallen} vs {lords, ravage}) -> 0.33 (Rejected)
            # "Lords of the Fallen" vs "Lords of the Fallen Deluxe" (Tokens: {lords, fallen} vs {lords, fallen}) -> 1.0 (Accepted)
            if score >= 0.5:
                matches.append(item)
            
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
                    # Optimistic approach: Keep the highest value to avoid false negatives
                    old_s = int(item.get('seeders') or 0)
                    old_l = int(item.get('leechers') or 0)
                    item['seeders'] = max(old_s, stats['seeders'])
                    item['leechers'] = max(old_l, stats['leechers'])
                else:
                    old_s = int(getattr(item, 'seeders', 0) or 0)
                    old_l = int(getattr(item, 'leechers', 0) or 0)
                    setattr(item, 'seeders', max(old_s, stats['seeders']))
                    setattr(item, 'leechers', max(old_l, stats['leechers']))

        # Process in parallel
        # Limit to avoid massive spam if list is huge, but usually candidates are few (<10)
        tasks = [process_item(c) for c in candidates]
        if tasks:
            await asyncio.gather(*tasks)

    @staticmethod
    @staticmethod
    def calculate_health_score(item: Item) -> Dict:
        """
        Calculates a health score based on Seeders/Leechers (if available/parsed).
        Uses PEERS (leechers) as fallback if seeders are 0 (valid in swarm-only networks).
        """
        # Extract seeders and leechers from the item (dict or object)
        if isinstance(item, dict):
            seeders = item.get('seeders')
            leechers = item.get('leechers')
        else:
            seeders = getattr(item, 'seeders', None)
            leechers = getattr(item, 'leechers', None)
            
        # Ensure integers
        try:
            seeders = int(seeders) if seeders is not None else 0
        except (ValueError, TypeError):
            seeders = 0
            
        try:
            leechers = int(leechers) if leechers is not None else 0
        except (ValueError, TypeError):
            leechers = 0
        
        # Check for Direct Download (HTTP/HTTPS) vs Magnet
        url = item.get('url') if isinstance(item, dict) else getattr(item, 'url', None)
        
        if url and not url.startswith('magnet:'):
            return {
                "score": 100,
                "label": "Direto",
                "color": "cyan",
                "seeders": 0,
                "leechers": 0,
                "is_direct": True
            }

        # Magnet Logic: Use seeders, but fallback to peers (leechers) if seeders=0
        # This handles swarm-only networks (common in GOG torrents)
        effective_count = seeders if seeders > 0 else leechers
        
        if effective_count >= 50:
            label = "Excelente" if seeders > 0 else f"Swarm Saudável ({leechers} peers)"
            return {"score": 100, "label": label, "color": "emerald", "seeders": seeders, "leechers": leechers}
        elif effective_count >= 20:
            label = "Bom" if seeders > 0 else f"Peers Ativos ({leechers})"
            return {"score": 75, "label": label, "color": "green", "seeders": seeders, "leechers": leechers}
        elif effective_count >= 5:
            label = "Regular" if seeders > 0 else f"Poucos Peers ({leechers})"
            return {"score": 50, "label": label, "color": "yellow", "seeders": seeders, "leechers": leechers}
        else:
            label = f"Fraco ({seeders} seeds)" if seeders > 0 else f"Crítico ({leechers} peers)"
            return {"score": 25, "label": label, "color": "red", "seeders": seeders, "leechers": leechers}
        # End of calculate_health_score

