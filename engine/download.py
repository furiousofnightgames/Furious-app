import os
import asyncio
import time
import httpx
import aiofiles
from typing import Optional, Callable


def log(msg: str):
    print(msg, flush=True)


# ============================================================
# SUPORTE A RANGE
# ============================================================

async def supports_range(url: str, verify: bool = True) -> dict:
    """
    Verifica se o servidor suporta downloads parciais e determina o tamanho REAL.
    Usa 'Range: bytes=0-0' para obter 'Content-Range', que é a fonte mais confiável de tamanho.
    """
    try:
        async with httpx.AsyncClient(verify=verify, timeout=httpx.Timeout(15, read=30), follow_redirects=True) as client:
            # Estrutura robusta: Tenta Range 0-0 primeiro (Melhor para tamanho exato)
            headers = {"Range": "bytes=0-0"}
            try:
                r = await client.get(url, headers=headers)
                
                # Check for Content-Range (Authoritative)
                content_range = r.headers.get("content-range", "")
                # Format: bytes 0-0/12345
                if r.status_code == 206 and "bytes" in content_range and "/" in content_range:
                    try:
                        size = int(content_range.split("/")[-1])
                        log(f"[INFO] Tamanho confirmado via Content-Range: {size} bytes")
                        return {
                            "accept_ranges": True,
                            "size": size,
                            "status_code": r.status_code
                        }
                    except:
                        pass
            except:
                pass

            # Fallback: HEAD request (Old methods)
            r = await client.head(url)
            # r.raise_for_status() # Don't raise, just analyze
            
            accept = r.headers.get("accept-ranges", "").lower()
            size_header = r.headers.get("content-length")
            size = int(size_header) if size_header else None
            
            # Se Range funcionou no HEAD (raro, mas possivel)
            if accept == "bytes":
                return {
                    "accept_ranges": True,
                    "size": size,
                    "status_code": r.status_code
                }
                
            return {
                "accept_ranges": accept == "bytes",
                "size": size,
                "status_code": r.status_code
            }
    except Exception as e:
        status_code = None
        if hasattr(e, 'response') and e.response:
            status_code = e.response.status_code
            
        return {
            "accept_ranges": False,
            "size": None,
            "status_code": status_code,
            "error": str(e)
        }


# ============================================================
# SERIAL – DOWNLOAD CLÁSSICO
# ============================================================

async def download_serial(
    url: str,
    dest_path: str,
    progress_cb: Optional[Callable] = None,
    resume: bool = True,
    verify: bool = True
):
    temp_path = dest_path + ".part"
    headers = {}
    existing = 0
    mode = "wb"

    # Resume
    if resume and os.path.exists(temp_path):
        existing = os.path.getsize(temp_path)
        headers["Range"] = f"bytes={existing}-"
        mode = "ab"

    try:
        async with httpx.AsyncClient(verify=verify, timeout=httpx.Timeout(30, read=300), follow_redirects=True) as client:
            async with client.stream("GET", url, headers=headers) as resp:
                resp.raise_for_status()

                ctype = resp.headers.get("content-type", "").lower()
                if "text/html" in ctype:
                    raise ValueError(
                        f"Este link nao e um download direto valido!\n"
                        f"O servidor retornou uma pagina HTML ao inves de um arquivo.\n"
                        f"Dica: Certifique-se de usar o link direto do arquivo, nao uma pagina de visualizacao.\n"
                        f"URL fornecida: {url}"
                    )


                cl = resp.headers.get("content-length")
                total = int(cl) + existing if cl else None
                downloaded = existing

                # Log de início
                filename = os.path.basename(dest_path)
                if total:
                    log(f"[DOWNLOAD SERIAL] {filename} - {total/1024/1024:.2f} MB")
                else:
                    log(f"[DOWNLOAD SERIAL] {filename} - tamanho desconhecido")

                start = time.time()
                last = start
                CHUNK = 4 * 1024 * 1024  # 4 MB

                # Inicializar UI com 0%
                if progress_cb and total:
                    await progress_cb(0, total)

                async with aiofiles.open(temp_path, mode) as f:
                    async for chunk in resp.aiter_bytes(chunk_size=CHUNK):
                        await f.write(chunk)
                        downloaded += len(chunk)

                        now = time.time()
                        # Reduzido para 0.5s para mostrar progresso em downloads rápidos
                        if total and (now - last >= 0.5):
                            spd = downloaded / (now - start)
                            pct = downloaded / total * 100
                            eta = (total - downloaded) / spd if spd > 0 else 0

                            log(f"[DL] {downloaded/1024/1024:.1f}/{total/1024/1024:.1f}MB "
                                f"({pct:.1f}%) | {spd/1024/1024:.1f} MB/s | "
                                f"ETA {int(eta//60)}m {int(eta%60):02d}s")
                            last = now

                            if progress_cb:
                                await progress_cb(downloaded, total)
    except httpx.HTTPStatusError as e:
        log(f"[ERRO] Status HTTP {e.response.status_code} para {url}")
        return None
    except Exception as e:
        log(f"[ERRO] Download falhou: {e}")
        return None

    os.replace(temp_path, dest_path)
    
    # Log de conclusão com estatísticas
    elapsed = time.time() - start
    avg_speed = downloaded / elapsed if elapsed > 0 else 0
    log(f"[CONCLUÍDO] {filename}")
    log(f"  Tamanho: {downloaded/1024/1024:.2f} MB")
    log(f"  Tempo: {elapsed:.1f}s")
    log(f"  Velocidade média: {avg_speed/1024/1024:.1f} MB/s")
    
    return dest_path


# ============================================================
# ULTRAMAX – MULTIWORKER
# ============================================================

async def download_segmented(
    url: str,
    dest_path: str,
    k: int = 4,
    n_conns: int = 8,
    progress_cb: Optional[Callable] = None,
    on_part_progress: Optional[Callable] = None,
    resume: bool = True,
    max_retries: int = 3,
    stop_event: Optional[asyncio.Event] = None,
    verify: bool = True,
    known_size: Optional[int] = None,
    preallocate: bool = False  # PERF: Disabled by default to avoid startup delay
):
    log(f"HTTP UltraMax: {url}")
    log(f"Destino: {dest_path}")

    # Tamanho do arquivo
    size = known_size
    if not size:
        try:
            # PERF: HTTP/2 enabled + reduced timeout for faster HEAD request
            async with httpx.AsyncClient(verify=verify, timeout=httpx.Timeout(10, read=30), follow_redirects=True, http2=True) as client:
                h = await client.head(url)
                h.raise_for_status()
                cl = h.headers.get("content-length")
                if not cl:
                    return await download_serial(url, dest_path, progress_cb)
                size = int(cl)
                log(f"Tamanho: {size/1024/1024:.2f} MB")
        except Exception as e:
            log(f"[WARN] Não foi possível obter tamanho via HEAD: {e}. Usando download serial.")
            return await download_serial(url, dest_path, progress_cb)
    else:
        log(f"Tamanho (cache): {size/1024/1024:.2f} MB")

    # Arquivos pequenos → Serial
    if size < 50 * 1024 * 1024:
        return await download_serial(url, dest_path, progress_cb)

    temp_path = dest_path + ".tmp"

    # PERF: Pré-alocar arquivo apenas se solicitado (evita delay de minutos no Windows)
    if preallocate:
        try:
            with open(temp_path, "wb") as f:
                f.seek(size - 1)
                f.write(b"\0")
            log(f" Arquivo pré-alocado: {size/1024/1024:.2f} MB")
        except Exception as e:
            log(f"[WARN] Pré-alocação falhou (continuando sem): {e}")
    else:
        # Create empty file - will grow as chunks are written
        open(temp_path, "wb").close()

    # PERF: Progressive chunk sizing - start small for quick feedback, grow for efficiency
    CHUNK_INITIAL = 4 * 1024 * 1024   # 4 MB for first 10% (quick progress)
    CHUNK_STEADY = 16 * 1024 * 1024    # 16 MB for rest (balanced I/O)
    CHUNK_BATCH_SIZE = 4  # PERF: Grab 4 chunks per lock acquisition to reduce contention
    
    # Restoring full power: 32 workers
    WORKERS = min(32, n_conns * 4) 
    log(f"Iniciando download com {WORKERS} workers simultâneos (Chunk progressivo 4-16MB, HTTP/2=ATIVADO)...")

    # Initialize UI with 0/total to avoid "unknown" state
    if progress_cb:
        await progress_cb(0, size)

    next_offset = 0
    downloaded_total = 0
    lock = asyncio.Lock()
    stop_flag = False
    active_workers = 0
    
    start_time = time.time()
    last_log = start_time

    connector_limits = httpx.Limits(
        max_connections=200,
        max_keepalive_connections=200,
        keepalive_expiry=300.0
    )

    # PERF: Use SINGLE shared client for all workers to avoid overhead of 32 SSL contexts
    # pooling is efficient this way.
    async with httpx.AsyncClient(
        verify=verify,
        timeout=httpx.Timeout(30, read=300),
        limits=connector_limits,
        follow_redirects=True,
        http2=True 
    ) as main_client:

        async def worker(wid: int):
            nonlocal next_offset, downloaded_total, stop_flag, last_log, active_workers
            
            # PERF: Quick staggered start
            await asyncio.sleep(wid * 0.005) 
            
            # Use shared client
            client = main_client
            active_workers += 1
            
            # log(f"[DEBUG] Worker {wid} iniciado")

            try:
                while True:
                    # Verificar se foi pausado/cancelado
                    if stop_event and stop_event.is_set():
                        stop_flag = True
                    if stop_flag:
                        break

                    # PERF: Batch chunk acquisition
                    chunks_to_download = []
                    
                    async with lock:
                        for _ in range(CHUNK_BATCH_SIZE):
                            if next_offset >= size:
                                break
                            
                            progress_pct = (next_offset / size) * 100 if size > 0 else 0
                            current_chunk_size = CHUNK_INITIAL if progress_pct < 10 else CHUNK_STEADY
                            
                            start = next_offset
                            end = min(start + current_chunk_size - 1, size - 1)
                            next_offset = end + 1
                            chunks_to_download.append((start, end))
                    
                    if not chunks_to_download:
                        break
                    
                    for start, end in chunks_to_download:
                        headers = {"Range": f"bytes={start}-{end}"}
                        expected_chunk_size = end - start + 1
                        
                        MAX_RETRIES = 5
                        success = False
                        
                        # Streaming direto para o disco para evitar "congelamento" visual e pico de memória
                        for attempt in range(MAX_RETRIES):
                            try:
                                # log(f"[DEBUG] W{wid} REQ {start}-{end}")
                                async with client.stream("GET", url, headers=headers) as r:
                                    if r.status_code not in (200, 206):
                                        log(f"[ERRO] HTTP {r.status_code} no worker {wid}")
                                        if r.status_code >= 500:
                                             raise Exception(f"Server error {r.status_code}")
                                        stop_flag = True
                                        return

                                    # Confirm connection established
                                    # log(f"[DEBUG] W{wid} HEADERS OK") 
                                    
                                    ctype = r.headers.get("content-type", "").lower()
                                    if "text/html" in ctype:
                                        log(f"[ERRO] Link invalido! Pagina HTML detectada.")
                                        stop_flag = True
                                        return

                                    bytes_read = 0
                                    
                                    async with aiofiles.open(temp_path, "r+b") as f:
                                        await f.seek(start)
                                        
                                        async for chunk in r.aiter_bytes(chunk_size=64*1024): # 64KB chunks
                                            if not chunk:
                                                break
                                            
                                            # CRITICAL: Check cancellation inside the inner loop!
                                            if stop_event and stop_event.is_set():
                                                stop_flag = True
                                                break
                                            if stop_flag:
                                                break

                                            # Write immediately
                                            await f.write(chunk)
                                            
                                            len_chunk = len(chunk)
                                            bytes_read += len_chunk
                                            
                                            # Update stats safely
                                            async with lock:
                                                downloaded_total += len_chunk
                                                now = time.time()
                                                # Log apenas a cada 1 segundo para não floodar
                                                if now - last_log >= 1:
                                                    elapsed = now - start_time
                                                    spd = downloaded_total / elapsed if elapsed > 0 else 0
                                                    pct = downloaded_total / size * 100
                                                    eta = (size - downloaded_total) / spd if spd > 0 else 0
                                                    log(f"[DL] {downloaded_total/1024/1024:.0f}/{size/1024/1024:.0f}MB "
                                                        f"({pct:.1f}%) | {spd/1024/1024:.1f} MB/s | "
                                                        f"Workers: {active_workers}/{WORKERS} | "
                                                        f"ETA {int(eta//60)}m {int(eta%60):02d}s")
                                                    last_log = now
                                                    if progress_cb:
                                                        await progress_cb(downloaded_total, size)
                                                    if on_part_progress:
                                                        await on_part_progress(0, downloaded_total, size)

                                            if bytes_read >= expected_chunk_size:
                                                break
                                            
                                            if stop_flag:
                                                break
                                
                                success = True
                                break
                            except Exception as e:
                                log(f"[DEBUG] W{wid} Error: {e}")
                                if attempt < MAX_RETRIES - 1:
                                    await asyncio.sleep(1)
                                else:
                                    stop_flag = True
                                    log(f"[ERRO] Worker {wid} falhou: {e}")
                                    return
                        
                        if not success:
                            break
                        
                        if stop_flag:
                             break

            finally:
                active_workers -= 1
                log(f"[DEBUG] Worker {wid} encerrado")

        tasks = [asyncio.create_task(worker(i)) for i in range(WORKERS)]
        
        if stop_event:
            # Create a wrapper for gather to wait on it
            # FIXED: gather returns a Future, do not wrap in create_task
            gather_task = asyncio.gather(*tasks, return_exceptions=True)
            stop_waiter = asyncio.create_task(stop_event.wait())
            
            # Race: Either all tasks finish OR stop_event is triggered
            done, _ = await asyncio.wait(
                [gather_task, stop_waiter], 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            if stop_waiter in done:
                log("[DEBUG] Cancelamento FORÇADO detectado. Parando workers...")
                stop_flag = True # Flag global
                for t in tasks:
                    if not t.done():
                        t.cancel()
                
                # Wait for tasks to handle cancellation (cleanup finally blocks)
                try:
                    await gather_task
                except:
                    pass
            else:
                # Tasks finished normally, cancel the waiter
                stop_waiter.cancel()
                try:
                    await stop_waiter
                except asyncio.CancelledError:
                    pass
            
            # Get results from the gather task
            results = await gather_task
        else:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for r in results:
            if isinstance(r, Exception) and not isinstance(r, asyncio.CancelledError):
                log(f"[CRÍTICO] Exceção não tratada no worker: {r}")

    # Verificação de integridade CRÍTICA
    if downloaded_total != size:
        was_cancelled = stop_flag or (stop_event and stop_event.is_set())
        
        if was_cancelled:
             log(f"[AVISO] Download interrompido pelo usuário. {downloaded_total}/{size} bytes.")
             # Não raise Exception se foi cancelado intencionalmente
             return

        error_msg = f"Download incompleto! Baixado: {downloaded_total}, Esperado: {size}"
        log(f"[ERRO] {error_msg}")
        
        # Limpar arquivo temporário se falhou
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        raise Exception(error_msg)

    os.replace(temp_path, dest_path)

    elapsed = time.time() - start_time
    avg = downloaded_total / elapsed if elapsed > 0 else 0
    
    success_msg = f"Concluído UltraMax: {size/1024/1024:.2f} MB em {elapsed:.1f}s ({avg/1024/1024:.1f} MB/s)"
    log(success_msg)
    log(f"Salvo: {dest_path}")

    return dest_path
