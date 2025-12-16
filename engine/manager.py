import asyncio
from typing import Optional, Callable, Dict
from backend.models.models import Job, Item, JobPart
from backend.db import get_session
from .download import download_serial, download_segmented, supports_range
from .aria2_wrapper import find_aria2_binary
import os
from backend import config as backend_config
import math
import json
import uuid
import time
from sqlmodel import select
from datetime import datetime
import re
import unicodedata
import errno

# job status: queued, running, paused, completed, failed


class JobManager:
    def __init__(self, concurrency: int = 2):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.concurrency = concurrency
        self.workers: list[asyncio.Task] = []
        self.running = False
        self._in_memory_progress: Dict[int, dict] = {}
        self._stop_tokens: Dict[int, asyncio.Event] = {}
        self._cancel_flags: Dict[int, bool] = {}  # Track if job was canceled (not paused)
        self._pause_flags: Dict[int, bool] = {}   # Track if job was explicitly paused (vs canceled)

    def _format_job_error(self, exc: Exception, tb: str, url: str, dest_to_save: Optional[str] = None) -> str:
        raw = str(exc) if exc is not None else ''
        combined_lower = (raw + "\n" + (tb or '')).lower() if (raw or tb) else ''
        err_no = getattr(exc, 'errno', None)
        winerror = getattr(exc, 'winerror', None)

        code = 'EUNKNOWN'
        title = 'Falha no download por um motivo não identificado.'
        hints: list[str] = [
            'Tente novamente.',
            'Se persistir, verifique sua conexão, espaço em disco e permissões de escrita no destino.'
        ]

        if isinstance(exc, FileNotFoundError) and ('aria2' in combined_lower or 'aria2c' in combined_lower):
            code = 'EARIA2_NOT_FOUND'
            title = 'aria2c não foi encontrado no sistema.'
            hints = [
                'Instale o aria2c e/ou configure o caminho (ARIA2C_PATH).',
                'Verifique a pasta portables/aria2-X.XX.X/ conforme instrução do app.'
            ]
        elif isinstance(exc, PermissionError) or err_no == errno.EACCES or 'permission denied' in combined_lower or 'acesso negado' in combined_lower:
            code = 'EACCES'
            title = 'Acesso negado ao gravar no destino (permissão insuficiente).' 
            hints = [
                'Escolha uma pasta onde você tenha permissão de escrita (ex.: dentro de Documentos/Downloads).',
                'Evite pastas protegidas do Windows (Program Files, Windows, etc.).',
                'Se estiver usando antivírus/Defender, teste adicionar exceção para a pasta de downloads.'
            ]
        elif isinstance(exc, FileExistsError) or err_no == errno.EEXIST or winerror == 183 or 'already exists' in combined_lower or 'file exists' in combined_lower or 'cannot create directory' in combined_lower or 'ja existe' in combined_lower:
            code = 'EDEST_EXISTS'
            title = 'Já existe uma pasta/arquivo com o mesmo nome no destino.'
            hints = [
                'Remova ou renomeie a pasta/arquivo existente no destino e tente novamente.',
                'Ou altere o nome do item/destino para criar uma pasta nova.'
            ]
        elif err_no == errno.ENOSPC or 'no space left' in combined_lower or 'espaco insuficiente' in combined_lower or 'not enough space' in combined_lower:
            code = 'ENOSPC'
            title = 'Espaço em disco insuficiente para concluir o download.'
            hints = [
                'Libere espaço no disco de destino e tente novamente.',
                'Se for torrent/magnet, considere deixar uma margem de espaço extra.'
            ]
        elif 'aria2 exit code' in combined_lower:
            m = re.search(r'aria2 exit code:\s*(\d+)', raw, re.IGNORECASE)
            exit_code = m.group(1) if m else None
            code = f'EARIA2_EXIT_{exit_code}' if exit_code else 'EARIA2_EXIT'
            title = 'O aria2 encerrou com erro durante o download.'
            hints = [
                'Verifique se existe pasta/arquivo conflitando no destino.',
                'Verifique permissões de escrita e espaço em disco.',
                'Se for torrent/magnet, pode haver problema no swarm (peers/seeders) ou bloqueio na rede.'
            ]
        elif 'erro ao acessar url' in combined_lower or ('status' in combined_lower and 'erro' in combined_lower):
            m = re.search(r'status\s+(\d+)', raw, re.IGNORECASE)
            status = m.group(1) if m else None
            code = f'EHTTP_{status}' if status else 'EHTTP'
            title = 'Não foi possível acessar o link (erro HTTP).' 
            hints = [
                'Verifique se o link ainda está válido e acessível no navegador.',
                'Alguns servidores bloqueiam downloads diretos e exigem link final do arquivo.'
            ]
        elif 'download stalled' in combined_lower or 'no progress' in combined_lower or 'stalled' in combined_lower:
            code = 'ESTALLED'
            title = 'O download ficou sem progresso por muito tempo (travou/sem peers/sem resposta).' 
            hints = [
                'Tente pausar e retomar.',
                'Se for torrent/magnet, pode ser falta de seeders/peers válidos ou bloqueio de rede.'
            ]
        elif 'destination files not found' in combined_lower:
            code = 'EDEST_NOT_FOUND'
            title = 'O download terminou, mas os arquivos finais não foram encontrados no destino.'
            hints = [
                'Verifique se a pasta de destino foi removida/movida por outro processo.',
                'Se houver antivírus/Defender, verifique se ele não colocou arquivos em quarentena.'
            ]

        lines: list[str] = [f"[Código: {code}]", title]
        if dest_to_save:
            lines.append(f"Destino: {dest_to_save}")
        if url:
            lines.append(f"URL: {url}")
        if hints:
            lines.append('')
            lines.append('Como resolver:')
            for h in hints:
                lines.append(f"- {h}")
        lines.append('')
        lines.append('--- Detalhes técnicos ---')
        if raw:
            lines.append(raw)
        if tb:
            lines.append(tb)
        return "\n".join(lines)

    async def start(self):
        if self.running:
            return
        self.running = True
        for _ in range(self.concurrency):
            t = asyncio.create_task(self._worker())
            self.workers.append(t)

    async def stop(self):
        self.running = False
        # Signal any running jobs to stop gracefully (important for aria2 subprocess)
        try:
            for job_id, ev in list(self._stop_tokens.items()):
                try:
                    ev.set()
                except Exception:
                    pass
        except Exception:
            pass

        # Give a short grace period for jobs to observe stop_event and terminate subprocesses
        try:
            await asyncio.sleep(0.5)
        except Exception:
            pass

        for w in self.workers:
            w.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []

    async def enqueue_job(self, job_id: int):
        await self.queue.put(job_id)

    async def _worker(self):
        while self.running:
            try:
                job_id = await self.queue.get()
            except asyncio.CancelledError:
                break
            try:
                await self._run_job(job_id)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Job failed: {e}")
            finally:
                self.queue.task_done()

    async def _run_job(self, job_id: int):
        # fetch job & item
        print(f"\nRUN _run_job({job_id}) - starting")
        
        # CRITICAL: Clear any residual state for this job_id (in case of ID reuse)
        if job_id in self._cancel_flags:
            del self._cancel_flags[job_id]
        if job_id in self._pause_flags:
            del self._pause_flags[job_id]
        if job_id in self._stop_tokens:
            del self._stop_tokens[job_id]
            
        session = get_session()
        j = session.get(Job, job_id)
        if not j:
            print(f"ERROR: Job #{job_id} not found in DB")
            return
        print(f"Job found: status={j.status}, item_id={j.item_id}")
        
        # set status running
        j.status = "running"
        j.last_error = None
        j.updated_at = datetime.utcnow()
        session.add(j)
        session.commit()
        print(f"Job status updated to 'running'")
        
        # get item
        it = session.get(Item, j.item_id)
        if not it:
            print(f"ERROR: Item #{j.item_id} not found in DB")
            j.status = "failed"
            j.last_error = "Item not found"
            session.add(j)
            session.commit()
            session.close()
            return

        print(f"Item found: {it.name} - URL: {it.url}")
        url = it.url
        dest = j.dest or backend_config.DOWNLOADS_DIR
        os.makedirs(dest, exist_ok=True)
        
        # Check if file already exists and is complete
        def sanitize_filename(name: str) -> str:
            if not name:
                return ''
            # normalize unicode and remove control/invalid chars for file systems (Windows)
            name = unicodedata.normalize('NFKC', str(name))
            # remove characters not allowed in Windows filenames
            name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
            # collapse whitespace
            name = re.sub(r'\s+', ' ', name).strip()
            # strip trailing dots and spaces
            name = name.rstrip('. ').strip()
            # limit length
            maxlen = 200
            if len(name) > maxlen:
                name = name[:maxlen]
            return name

        raw_name = os.path.basename(it.url.split("?")[0]) or it.name or f"download_{job_id}"
        filename = sanitize_filename(raw_name) or f"download_{job_id}"
        
        # Se o nome foi customizado (diferente do nome original da URL), criar pasta
        original_filename = os.path.basename(it.url.split("?")[0])
        is_custom_name = it.name and it.name != original_filename
        
        # Determine what path to save to database for deletion
        dest_to_save = None
        
        if url.startswith("magnet:"):
            raw_name = it.name or f"job_{job_id}"
            filename = sanitize_filename(raw_name) or f"job_{job_id}"
            dest_path = os.path.join(dest, filename)
            dest_to_save = dest_path
        else:
            if is_custom_name:
                # Criar pasta com nome customizado, arquivo original dentro
                custom_folder = sanitize_filename(it.name) or f"download_{job_id}"
                dest_path = os.path.join(dest, custom_folder, original_filename)
                dest_to_save = os.path.join(dest, custom_folder)  # Save the folder for deletion
                # Criar pasta de forma assíncrona (não bloqueia início)
                try:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    print(f" Pasta customizada criada: {custom_folder}/")
                except Exception as e:
                    print(f"Aviso ao criar pasta: {e}")
            else:
                # Sem nome customizado
                # CRITICAL FIX: Se 'dest' já for o caminho completo (termina com filename), não concatenar
                if str(dest).endswith(filename) or (os.path.splitext(dest)[1] and not os.path.isdir(dest)):
                    dest_path = dest
                else:
                    dest_path = os.path.join(dest, filename)
                
                dest_to_save = dest_path
        
        print(f"Dest: {dest_path}")

        # Se arquivo já existe, criar novo nome (não sobrescrever)
        if os.path.exists(dest_path) and not url.startswith("magnet:"):
            base, ext = os.path.splitext(dest_path)
            counter = 1
            while os.path.exists(f"{base}_{counter}{ext}"):
                counter += 1
            dest_path = f"{base}_{counter}{ext}"
            dest_to_save = dest_path  # CRITICAL: Update dest_to_save with renamed path
            print(f" Arquivo já existe, salvando como: {os.path.basename(dest_path)}")
        
        
        stop_event = asyncio.Event()
        self._stop_tokens[job_id] = stop_event

        async def progress_cb(downloaded, total, peers=0, seeders=0, speed=None, phase=None, phase_label=None, phase_progress=None):
            import time as time_module
            p = (downloaded / total * 100) if total and total > 0 else None
            now_ts = time_module.time()
            info = self._in_memory_progress.get(job_id, {})
            last_ts = info.get("last_ts", now_ts)
            last_bytes = info.get("last_bytes", downloaded)
            
            # If speed is provided by the engine (e.g. aria2), use it directly
            # Otherwise, calculate it manually (less accurate)
            if speed is None:
                dt = now_ts - last_ts if now_ts > last_ts else 1e-6
                calc_speed = (downloaded - last_bytes) / dt if dt > 0 else 0
                # Clamp unrealistic speeds (> 500MB/s) likely due to resume/disk check
                if calc_speed > 500 * 1024 * 1024: 
                    speed = info.get("speed", 0) # Use previous speed
                else:
                    speed = calc_speed
            
            info.update({"downloaded": downloaded, "total": total, "progress": p, "speed": speed, "peers": peers, "seeders": seeders, "last_ts": now_ts, "last_bytes": downloaded})
            if phase is not None:
                info["phase"] = phase
            if phase_label is not None:
                info["phase_label"] = phase_label
            if phase_progress is not None:
                info["phase_progress"] = phase_progress
            self._in_memory_progress[job_id] = info
            # update DB periodically (less frequently to minimize writes)
            await asyncio.to_thread(self._update_job_db, job_id, p)

        try:
            if url.startswith("magnet:"):
                # detect aria2 binary (prefer backend config path)
                from backend import config as backend_config
                # Determine project root relative to this file (robust when backend is started from elsewhere)
                try:
                    from pathlib import Path
                    project_root = str(Path(__file__).resolve().parent.parent)
                except Exception:
                    project_root = os.getcwd()
                aria_path = backend_config.ARIA2C_PATH or find_aria2_binary(project_root)
                if not aria_path or not os.path.exists(aria_path):
                    msg = self._format_job_error(
                        FileNotFoundError('aria2c binary not found'),
                        tb='',
                        url=url,
                        dest_to_save=dest_to_save
                    )
                    j.status = "failed"
                    j.last_error = msg
                    j.updated_at = datetime.utcnow()
                    session.add(j)
                    session.commit()
                    session.close()
                    return

                # Download magnet using aria2 CLI (not RPC)
                from .aria2_wrapper import download_magnet_cli

                try:
                    result = await download_magnet_cli(
                        url,
                        dest_path,
                        progress_cb=progress_cb,
                        stop_event=stop_event,
                        aria2_path=aria_path,
                        project_root=project_root,
                        total_size_hint=it.size,  # Pass item's known size
                        job_id=job_id,  # Pass job_id to track cancel vs pause
                        job_manager=self  # Pass job_manager to check cancel status
                    )
                    
                    # Result is now a tuple (final_path, status)
                    if isinstance(result, tuple):
                        final_path, download_status = result
                    else:
                        # Fallback for old behavior
                        final_path = result
                        download_status = "completed"
                    
                    # Handle based on the actual status returned by aria2_wrapper
                    if download_status == "paused":
                        # Job was paused
                        j.status = "paused"
                        j.updated_at = datetime.utcnow()
                        session.add(j)
                        session.commit()
                        print(f"Download paused, will resume later")
                    elif download_status == "canceled":
                        # Job was canceled
                        session.refresh(j)
                        # Always try to save the actual download path, not just the base folder
                        # Even if aria2 was canceled before detecting path, try to find partial files
                        actual_dest = final_path if final_path else dest_path
                        
                        # If final_path is empty/base folder, try to find the actual folder
                        if not final_path or final_path == dest_path:
                            try:
                                from pathlib import Path as PathlibPath
                                parent = PathlibPath(dest_path).parent
                                # Look for recently created folders (likely the download folder)
                                if parent.exists():
                                    candidates = []
                                    for item in parent.iterdir():
                                        if item.is_dir() and not item.name.startswith('.'):
                                            try:
                                                mtime = item.stat().st_mtime
                                                import time
                                                # If created in last 60 seconds, it's likely our download
                                                if (time.time() - mtime) < 60:
                                                    candidates.append(item)
                                            except:
                                                pass
                                    
                                    if candidates:
                                        # Use the most recently modified one
                                        candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                                        actual_dest = str(candidates[0])
                                        print(f"   Found partial download folder: {actual_dest}")
                            except Exception as e:
                                print(f"   Could not find partial download folder: {e}")
                        
                        j.dest = actual_dest
                        j.updated_at = datetime.utcnow()
                        session.add(j)
                        session.commit()
                        print(f"Download was canceled, keeping status as canceled (DB status: {j.status})")
                        print(f"   Saved real dest for cleanup: {j.dest}")
                    else:
                        # Download completed successfully
                        j.status = "completed"
                        j.progress = 100.0
                        j.dest = final_path if final_path else dest_path
                        dest_to_save = final_path if final_path else dest_path
                        
                        # Calculate and save actual file size
                        try:
                            actual_path = final_path if final_path else dest_path
                            if os.path.isfile(actual_path):
                                j.size = os.path.getsize(actual_path)
                            elif os.path.isdir(actual_path):
                                # Sum all files in directory
                                total_size = 0
                                for root, dirs, files in os.walk(actual_path):
                                    for file in files:
                                        total_size += os.path.getsize(os.path.join(root, file))
                                j.size = total_size
                            print(f"[OK] Saved download size: {j.size} bytes ({j.size / 1024 / 1024 / 1024:.2f} GB)" if j.size else "[OK] Download completed (size unknown)")
                        except Exception as e:
                            print(f"[WARN] Could not calculate size: {e}")
                        
                        j.updated_at = datetime.utcnow()
                        session.add(j)
                        session.commit()
                except Exception as e:
                    j.status = "failed"
                    j.last_error = str(e)
                    j.updated_at = datetime.utcnow()
                    session.add(j)
                    session.commit()
                    raise
            else:
                # other urls: use size from item if available, otherwise discover
                size = it.size if it.size and it.size > 0 else None
                accept_range = True  # Assume support unless proven otherwise
                
                # Try segmented first if size is known and large enough
                if size and size > 1_000_000:
                    # Start download immediately with segmented (even before confirming range support)
                    k = j.k or 4
                    n_conns = j.n_conns or 4
                    try:
                        await self._download_segmented_job(j, url, dest_path, k=k, n_conns=n_conns, progress_cb=progress_cb, resume=j.resume_on_start, verify=j.verify_ssl)
                    except Exception as e:
                        # Segmented failed (maybe no range support), fall back to serial
                        print(f"Segmented failed ({e}), falling back to serial download...")
                        await download_serial(url, dest_path, progress_cb=progress_cb, resume=j.resume_on_start, verify=j.verify_ssl)
                else:
                    # Size unknown or too small - discover it
                    info = await supports_range(url, verify=j.verify_ssl)
                    
                    # CRITICAL FIX: Check for HTTP errors/exceptions immediately
                    if info.get("error") or (info.get("status_code") and info.get("status_code") >= 400):
                        raise Exception(f"Erro ao acessar URL: Status {info.get('status_code')} - {info.get('error', 'Unknown Error')}")
                        
                    size = info.get("size")
                    accept_range = info.get("accept_ranges")
                    
                    if accept_range and size and size > 1_000_000:
                        # segmented - use job configured k/n_conns
                        k = j.k or 4
                        n_conns = j.n_conns or 4
                        await self._download_segmented_job(j, url, dest_path, k=k, n_conns=n_conns, progress_cb=progress_cb, resume=j.resume_on_start, verify=j.verify_ssl)
                    else:
                        await download_serial(url, dest_path, progress_cb=progress_cb, resume=j.resume_on_start, verify=j.verify_ssl)
                # check if stop was requested
                if stop_event and stop_event.is_set():
                    j.status = "paused"
                    print(f"[PAUSE] Job #{job_id} pausado pelo usuário")
                else:
                    j.status = "completed"
                    # Save the path (folder if custom name, file path otherwise) for deletion
                    j.dest = dest_to_save
                    print(f"[DEBUG] Salvando job.dest = {dest_to_save}")
                    
                    # Calculate and save actual file size
                    try:
                        if os.path.isfile(dest_to_save):
                            j.size = os.path.getsize(dest_to_save)
                        elif os.path.isdir(dest_to_save):
                            # Sum all files in directory
                            total_size = 0
                            for root, dirs, files in os.walk(dest_to_save):
                                for file in files:
                                    total_size += os.path.getsize(os.path.join(root, file))
                            j.size = total_size
                        print(f"[OK] Saved download size: {j.size} bytes ({j.size / 1024 / 1024 / 1024:.2f} GB)")
                    except Exception as e:
                        print(f"[WARN] Could not calculate size: {e}")
                
                j.progress = 100.0
                j.updated_at = datetime.utcnow()
                session.add(j)
                session.commit()
        except Exception as e:
            # record failure
            import traceback
            traceback.print_exc()
            # persist last error message to DB to aid debugging (include traceback)
            tb = traceback.format_exc()
            try:
                j.last_error = self._format_job_error(e, tb=tb, url=url, dest_to_save=dest_to_save)
            except Exception:
                pass
            j.status = "failed"
            # Save the path for deletion purposes
            j.dest = dest_to_save
            j.updated_at = datetime.utcnow()
            session.add(j)
            session.commit()
            try:
                session.close()
            except Exception:
                pass
        finally:
            # cleanup
            if job_id in self._stop_tokens:
                del self._stop_tokens[job_id]
            # Remove from memory progress
            if job_id in self._in_memory_progress:
                del self._in_memory_progress[job_id]
            # Clean up metadata files after download (success or failure)
            # Use dest_to_save which contains the actual path where download happened
            try:
                await self._cleanup_partial_files(dest_to_save, job_id)
            except Exception as e:
                print(f"[WARN] Error during final cleanup: {e}")

    async def _cleanup_partial_files(self, dest_path: str, job_id: int):
        """Clean up partial files and metadata residuals from downloads"""
        import shutil
        
        try:
            # Clean up .part file if exists
            if os.path.exists(dest_path + ".part"):
                os.remove(dest_path + ".part")
                print(f"[OK] Removed partial file: {dest_path}.part")
        except Exception as e:
            print(f"[WARN] Could not remove {dest_path}.part: {e}")
        
        try:
            # Clean up .parts directory if exists
            part_dir = dest_path + ".parts"
            if os.path.isdir(part_dir):
                shutil.rmtree(part_dir)
                print(f"[OK] Removed parts directory: {part_dir}")
        except Exception as e:
            print(f"[WARN] Could not remove parts directory: {e}")
        
        # Clean up torrent/aria2 metadata files
        for suffix in ['.aria2', '.aria2c', '.torrent']:
            try:
                meta_file = dest_path + suffix
                if os.path.exists(meta_file):
                    os.remove(meta_file)
                    print(f"[OK] Removed metadata: {meta_file}")
            except Exception as e:
                print(f"[WARN] Could not remove {dest_path}{suffix}: {e}")
        
        # For torrents: if dest_path is a folder, remove .aria2 and .aria2c files inside it too
        try:
            if os.path.isdir(dest_path):
                for filename in os.listdir(dest_path):
                    if filename.endswith(('.aria2', '.aria2c')):
                        meta_path = os.path.join(dest_path, filename)
                        try:
                            os.remove(meta_path)
                            print(f"[OK] Removed metadata inside folder: {meta_path}")
                        except Exception as e:
                            print(f"[WARN] Could not remove {meta_path}: {e}")
        except Exception as e:
            print(f"[WARN] Error checking folder for metadata: {e}")
        
        # Also clean up .torrent files from parent directory (for torrents downloaded with aria2)
        try:
            parent_dir = os.path.dirname(dest_path)
            if os.path.isdir(parent_dir):
                for filename in os.listdir(parent_dir):
                    if filename.endswith('.torrent'):
                        torrent_path = os.path.join(parent_dir, filename)
                        try:
                            os.remove(torrent_path)
                            print(f"[OK] Removed torrent metadata: {torrent_path}")
                        except Exception as e:
                            print(f"[WARN] Could not remove {torrent_path}: {e}")
        except Exception as e:
            print(f"[WARN] Error cleaning parent directory for torrent files: {e}")

    async def _download_segmented_job(self, job: Job, url: str, dest_path: str, k: int, n_conns: int, progress_cb: Optional[Callable], resume: bool = True, verify: bool = True):
        session = get_session()
        
        # Get size from item if available
        size = None
        item = session.exec(select(Item).where(Item.id == job.item_id)).one_or_none() if job.item_id else None
        if item and item.size and item.size > 0:
            size = item.size
        
        session.close()
        
        # Create parts in background (don't block download)
        async def create_parts_async():
            try:
                if not size or size <= 1_000_000:
                    return  # Skip part creation for small files
                    
                session = get_session()
                part_size = math.ceil(size / k)
                for i in range(k):
                    s = i * part_size
                    e = min((i + 1) * part_size - 1, size - 1)
                    existing = session.exec(
                        select(JobPart).where(
                            (JobPart.job_id == job.id) & (JobPart.index == i)
                        )
                    ).one_or_none()
                    
                    if not existing:
                        p = JobPart(
                            job_id=job.id, 
                            index=i, 
                            start=s, 
                            end=e, 
                            downloaded=0, 
                            path=os.path.join(dest_path + ".parts", f"part_{i}"), 
                            size=(e - s + 1), 
                            status="pending"
                        )
                        session.add(p)
                session.commit()
                print(f" Created {k} JobParts for segmented download (total size: {size} bytes)")
                session.close()
            except Exception as e:
                print(f"Error creating JobParts: {e}")
        
        # Start creating parts in background immediately
        asyncio.create_task(create_parts_async())
        
        # Start download immediately without waiting for parts creation
        await self._start_download(job, url, dest_path, size, k, n_conns, progress_cb, resume, verify)

    async def _start_download(self, job: Job, url: str, dest_path: str, size: Optional[int], k: int, n_conns: int, progress_cb: Optional[Callable], resume: bool, verify: bool):
        """Start the actual download immediately"""
        session = get_session()
        jp_list = session.exec(select(JobPart).where(JobPart.job_id == job.id)).all()
        session.close()
        
        if not size:
            try:
                # Try to get size without blocking - use short timeout
                info = await asyncio.wait_for(supports_range(url, verify=verify), timeout=3.0)
                size = info.get("size")
            except asyncio.TimeoutError:
                print(f"Timeout getting file size, will discover during download")
            except Exception as e:
                print(f"Could not get file size: {e}, will discover during download")


        # perform segmented download using underlying engine.download functions and update DB accordingly
        async def on_part_progress(index, downloaded_bytes, part_total):
            # update JobPart downloaded size in DB
            try:
                session_up = get_session()
                part = session_up.exec(select(JobPart).where((JobPart.job_id == job.id) & (JobPart.index == index))).one_or_none()
                if part:
                    part.downloaded = min(downloaded_bytes, part.size or downloaded_bytes)
                    if downloaded_bytes >= (part.size or 0) if part.size else False:
                        part.status = "completed"
                    else:
                        part.status = "running"
                    part.updated_at = datetime.utcnow()
                    session_up.add(part)
                    session_up.commit()
            except Exception as e:
                print(f"Error updating JobPart progress: {e}")
            finally:
                try:
                    session_up.close()
                except Exception:
                    pass

        stop_event = self._stop_tokens.get(job.id)
        try:
            await download_segmented(url, dest_path, k=k, n_conns=n_conns, progress_cb=progress_cb, on_part_progress=on_part_progress, resume=resume, stop_event=stop_event, verify=verify, known_size=size)
        except Exception as e:
            print(f" Segmented download failed: {e}")
            # Mark all parts as failed
            session = get_session()
            parts = session.exec(select(JobPart).where(JobPart.job_id == job.id)).all()
            for p in parts:
                p.status = "failed"
                session.add(p)
            session.commit()
            session.close()
            raise
        
        # update JobParts DB: mark as downloaded
        session = get_session()
        parts = session.exec(select(JobPart).where(JobPart.job_id == job.id)).all()
        for p in parts:
            p.downloaded = p.size
            p.status = "completed"
            p.updated_at = datetime.utcnow()
            session.add(p)
        session.commit()
        session.close()
        print(f" All JobParts marked as completed")

    def _update_job_db(self, job_id, progress):
        session = get_session()
        j = session.get(Job, job_id)
        if not j:
            return
        if progress is not None:
            j.progress = progress
        j.updated_at = datetime.utcnow()
        session.add(j)
        session.commit()
        try:
            session.close()
        except Exception:
            pass

    def get_progress(self, job_id: int) -> dict:
        return self._in_memory_progress.get(job_id, {})

    def stop_job(self, job_id: int, cancel: bool = False, pause: bool = False):
        """Stop a job. If cancel=True, mark as canceled. If pause=True, mark as paused."""
        e = self._stop_tokens.get(job_id)
        if not e:
            e = asyncio.Event()
            self._stop_tokens[job_id] = e
        e.set()
        if cancel:
            self._cancel_flags[job_id] = True
        elif pause:
            self._pause_flags[job_id] = True
    
    def is_job_canceled(self, job_id: int) -> bool:
        """Check if job was canceled (not just paused)."""
        return self._cancel_flags.get(job_id, False)
    
    def is_job_paused(self, job_id: int) -> bool:
        """Check if job was explicitly paused (vs canceled)."""
        return self._pause_flags.get(job_id, False)


job_manager = JobManager(concurrency=1)
