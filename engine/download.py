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
    """Verifica se o servidor suporta downloads parciais."""
    try:
        async with httpx.AsyncClient(verify=verify, timeout=httpx.Timeout(30, read=60), follow_redirects=True) as client:
            r = await client.head(url)
            r.raise_for_status()
            accept = r.headers.get("accept-ranges", "").lower()
            size = r.headers.get("content-length")
            size = int(size) if size else None
            return {
                "accept_ranges": accept == "bytes",
                "size": size,
                "status_code": r.status_code
            }
    except Exception as e:
        status_code = None
        # Tenta extrair status code se for erro HTTP
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
    known_size: Optional[int] = None
):
    log(f"HTTP UltraMax: {url}")
    log(f"Destino: {dest_path}")

    # Tamanho do arquivo
    size = known_size
    if not size:
        try:
            async with httpx.AsyncClient(verify=verify, timeout=httpx.Timeout(30, read=60), follow_redirects=True, http2=False) as client:
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

    # Pré-alocar arquivo
    with open(temp_path, "wb") as f:
        f.seek(size - 1)
        f.write(b"\0")

    CHUNK = 32 * 1024 * 1024  # 32 MB (Balanceado para I/O e rede)
    # Ajustado para 32 workers após testes reais mostrarem gargalo com 64
    WORKERS = min(32, n_conns * 4) 
    log(f"Iniciando download com {WORKERS} workers simultâneos (Chunk {CHUNK/1024/1024:.0f}MB, HTTP/2={'ATIVADO' if True else 'DESATIVADO'})...")

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

    async def worker(wid: int):
        nonlocal next_offset, downloaded_total, stop_flag, last_log, active_workers
        
        # Staggered start: evita "congelamento" inicial abrindo conexões aos poucos
        await asyncio.sleep(wid * 0.05) 
        
        async with httpx.AsyncClient(
            verify=verify,
            timeout=httpx.Timeout(30, read=300),
            limits=connector_limits,
            follow_redirects=True,
            http2=True
        ) as client:
            active_workers += 1
            while True:
                # Verificar se foi pausado/cancelado
                if stop_event and stop_event.is_set():
                    stop_flag = True
                if stop_flag:
                    break

                async with lock:
                    if next_offset >= size:
                        break
                    start = next_offset
                    end = min(start + CHUNK - 1, size - 1)
                    next_offset = end + 1
                    
                headers = {"Range": f"bytes={start}-{end}"}
                buffer = bytearray()
                expected_chunk_size = end - start + 1  # Tamanho exato que devemos baixar

                # Tentativa de retry para robustez
                MAX_RETRIES = 5
                success = False
                for attempt in range(MAX_RETRIES):
                    try:
                        async with client.stream("GET", url, headers=headers) as r:
                            if r.status_code not in (200, 206):
                                if r.status_code >= 500:
                                     raise Exception(f"Server error {r.status_code}")
                                
                                stop_flag = True
                                log(f"[ERRO] HTTP {r.status_code} no worker {wid}")
                                return

                            ctype = r.headers.get("content-type", "").lower()
                            if "text/html" in ctype:
                                stop_flag = True
                                log(f"[ERRO] Link invalido! Pagina HTML detectada.")
                                return

                            # CRITICAL: Limit bytes read to prevent over-fetching
                            bytes_read = 0
                            async for chunk in r.aiter_bytes(chunk_size=1024*1024):
                                bytes_to_add = min(len(chunk), expected_chunk_size - bytes_read)
                                if bytes_to_add > 0:
                                    buffer.extend(chunk[:bytes_to_add])
                                    bytes_read += bytes_to_add
                                
                                if bytes_read >= expected_chunk_size:
                                    break  # Stop reading if we got all we need
                        
                        success = True
                        break

                    except Exception as e:
                        if attempt < MAX_RETRIES - 1:
                            delay = (attempt + 1) * 2
                            await asyncio.sleep(delay)
                        else:
                            stop_flag = True
                            log(f"[ERRO] Worker {wid} falhou definitivamente: {e}")
                            return
                
                if not success:
                    break

                # Escrevendo no disco
                try:
                    with open(temp_path, "r+b") as f:
                        f.seek(start)
                        f.write(buffer)
                except Exception as e:
                    log(f"[ERRO] Erro de escrita IO no worker {wid}: {e}")
                    stop_flag = True
                    return

                async with lock:
                    downloaded_total += len(buffer)
                    now = time.time()
                    if now - last_log >= 1:
                        elapsed = now - start_time
                        spd = downloaded_total / elapsed if elapsed > 0 else 0
                        pct = downloaded_total / size * 100
                        eta = (size - downloaded_total) / spd if spd > 0 else 0
                        
                        # Log mais rico
                        log(f"[DL] {downloaded_total/1024/1024:.0f}/{size/1024/1024:.0f}MB "
                            f"({pct:.1f}%) | {spd/1024/1024:.1f} MB/s | "
                            f"Workers: {active_workers}/{WORKERS} | "
                            f"ETA {int(eta//60)}m {int(eta%60):02d}s")
                        
                        last_log = now
                        if progress_cb:
                            await progress_cb(downloaded_total, size)
                        
                        if on_part_progress:
                            await on_part_progress(0, downloaded_total, size)
            
            active_workers -= 1

    tasks = [asyncio.create_task(worker(i)) for i in range(WORKERS)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for r in results:
        if isinstance(r, Exception):
            log(f"[CRÍTICO] Exceção não tratada no worker: {r}")

    # Verificação de integridade CRÍTICA
    if downloaded_total != size:
        error_msg = f"Download incompleto! Baixado: {downloaded_total}, Esperado: {size}"
        if stop_flag:
            error_msg += " (Interrompido por erro nos workers)"
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
