import asyncio
import struct
import socket
import random
import time
from urllib.parse import urlparse

class UDPTrackerClient:
    def __init__(self, timeout=1.5, retries=1):
        self.timeout = timeout
        self.retries = retries
        self.connection_id = 0x41727101980  # Magic constant for connection ID

    async def get_stats(self, magnet_link):
        """
        Extracts trackers from magnet link and queries them for seeds/peers.
        Returns a dict with 'seeders' and 'leechers' (max values found).
        """
        info_hash = self._extract_info_hash(magnet_link)
        if not info_hash:
            print("[Tracker] Erro: Não foi possível extrair hash do magnet link.")
            return None

        trackers = self._extract_trackers(magnet_link)
        if not trackers:
            print("[Tracker] Aviso: Nenhum tracker UDP encontrado no magnet link.")
            return None

        print(f"[Tracker] Sondando {len(trackers)} trackers para hash {info_hash.hex()}...")

        # Query trackers in parallel
        tasks = [self._scrape_tracker(tracker, info_hash) for tracker in trackers]
        
        # Wait for all, but don't crash if some fail
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        max_seeds = 0
        max_peers = 0
        success = False

        for res in results:
            if isinstance(res, dict) and res:
                success = True
                if res['seeds'] > max_seeds:
                    max_seeds = res['seeds']
                if res['peers'] > max_peers:
                    max_peers = res['peers']
            elif isinstance(res, Exception):
                pass 
                # print(f"[Tracker] Falha em tarefa: {res}")

        if not success:
            print("[Tracker] Falha: Nenhum tracker respondeu com sucesso.")
            return None

        print(f"[Tracker] Sucesso! Seeds: {max_seeds}, Peers: {max_peers}")
        return {"seeders": max_seeds, "leechers": max_peers}

    def _extract_info_hash(self, magnet_link):
        try:
            # simple extraction for urn:btih:HASH
            if "urn:btih:" not in magnet_link:
                return None
            
            start = magnet_link.find("urn:btih:") + 9
            end = magnet_link.find("&", start)
            if end == -1:
                end = len(magnet_link)
            
            hash_str = magnet_link[start:end]
            if len(hash_str) == 32: # Base32
                 import base64
                 return base64.b32decode(hash_str.upper())
            elif len(hash_str) == 40: # Hex
                return bytes.fromhex(hash_str)
            return None
        except Exception:
            return None

    def _extract_trackers(self, magnet_link):
        trackers = []
        try:
            parts = magnet_link.split("&tr=")
            for t in parts[1:]:
                # URL decode
                from urllib.parse import unquote
                url = unquote(t.split("&")[0])
                if url.startswith("udp://"):
                    trackers.append(url)
        except Exception:
            pass
        return trackers

    async def _scrape_tracker(self, tracker_url, info_hash):
        parsed = urlparse(tracker_url)
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return None

        try:
            # Create socket
            loop = asyncio.get_running_loop()
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: TrackerProtocol(),
                remote_addr=(host, port)
            )
            
            try:
                # 1. Connect
                transaction_id = random.randint(0, 65535)
                connect_req = struct.pack("!QII", self.connection_id, 0, transaction_id)
                transport.sendto(connect_req)
                
                # Wait for response
                data = await asyncio.wait_for(protocol.response_future, self.timeout)
                
                if len(data) < 16:
                    print(f"[Tracker] {host} Erro: Resposta curta no Connect ({len(data)} bytes)")
                    return None
                    
                action, res_trans_id, conn_id = struct.unpack("!IIQ", data[:16])
                
                if res_trans_id != transaction_id:
                    print(f"[Tracker] {host} Erro: Transaction ID mismatch no Connect")
                    return None
                
                # 2. Scrape
                # Reset for next packet
                protocol.response_future = asyncio.Future()
                
                transaction_id = random.randint(0, 65535)
                scrape_req = struct.pack("!QII20s", conn_id, 2, transaction_id, info_hash)
                transport.sendto(scrape_req)
                
                data = await asyncio.wait_for(protocol.response_future, self.timeout)
                
                if len(data) < 8:
                    print(f"[Tracker] {host} Erro: Resposta curta no Scrape")
                    return None
                    
                action, res_trans_id = struct.unpack("!II", data[:8])
                
                if res_trans_id != transaction_id:
                    print(f"[Tracker] {host} Erro: Transaction ID mismatch no Scrape")
                    return None
                
                if len(data) >= 20:
                    seeds, completed, leechers = struct.unpack("!III", data[8:20])
                    
                    # Sanity Check: Valores absurdos (ex: > 500.000) geralmente são bugs do tracker ou overflow
                    if seeds > 500000 or leechers > 500000:
                         print(f"[Tracker] {host} IGNORADO: Valores suspeitos (Seeds={seeds}, Peers={leechers})")
                         return None

                    print(f"[Tracker] {host} OK! Seeds={seeds} Peers={leechers}")
                    return {"seeds": seeds, "peers": leechers}
                else:
                    print(f"[Tracker] {host} Erro: Dados insuficientes no Scrape ({len(data)})")
                    return None
                    
            except asyncio.TimeoutError:
                # print(f"[Tracker] {host} warn: Timeout ({self.timeout}s)")
                return None
            except Exception as e:
                # print(f"[Tracker] {host} Erro: {e}")
                return None
            finally:
                transport.close()
                
        except Exception as e:
            # print(f"[Tracker] {host} Falha Socket: {e}")
            return None

class TrackerProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.response_future = asyncio.Future()

    def datagram_received(self, data, addr):
        if not self.response_future.done():
            self.response_future.set_result(data)

    def error_received(self, exc):
        if not self.response_future.done():
            self.response_future.set_exception(exc)

    def connection_lost(self, exc):
        if not self.response_future.done():
            self.response_future.set_exception(Exception("Connection lost"))
