import shutil
import subprocess
import os
from collections import deque
from typing import Optional, List, Tuple, Dict, Any
import sys
import time
import httpx
import asyncio
import aiofiles
from pathlib import Path
import threading
import xml.etree.ElementTree as ET
import re


def _get_aria2_paths() -> tuple[Path, Path]:
    session_env = os.environ.get("ARIA2_SESSION_FILE")
    dht_env = os.environ.get("ARIA2_DHT_FILE")
    app_data_dir = os.environ.get("APP_DATA_DIR")
    if session_env:
        session_file = Path(session_env)
    elif app_data_dir:
        try:
            os.makedirs(app_data_dir, exist_ok=True)
        except Exception:
            pass
        session_file = Path(app_data_dir) / "aria2.session"
    else:
        session_file = Path("aria2.session")

    if dht_env:
        dht_file = Path(dht_env)
    elif app_data_dir:
        dht_file = Path(app_data_dir) / "dht.dat"
    else:
        dht_file = Path("dht.dat")

    return session_file, dht_file


# Lista de trackers públicos confiáveis para maximizar peers/seeders
# Estes trackers são injetados automaticamente em todos os downloads magnet
TRACKERS_EXTRAS = [
    # Tier 1: Trackers mais populares e estáveis
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://exodus.desync.com:6969/announce",
    "udp://tracker.moeking.me:6969/announce",
    
    # Tier 2: Trackers públicos bem estabelecidos
    "udp://tracker.openbittorrent.com:6969/announce",
    "udp://opentracker.i2p.rocks:6969/announce",
    "udp://tracker.internetwarriors.net:1337/announce",
    "udp://explodie.org:6969/announce",
    "udp://tracker.cyberia.is:6969/announce",
    
    # Tier 3: Trackers adicionais confiáveis
    "udp://tracker.birkenwald.de:6969/announce",
    "udp://tracker.tiny-vps.com:6969/announce",
    "udp://retracker.lanta-net.ru:2710/announce",
    "udp://ipv4.tracker.harry.lu:80/announce",
    "udp://tracker.theoks.net:6969/announce",
    "udp://tracker.ccp.ovh:6969/announce",
    
    # Tier 4: Internet Archive (sem fins lucrativos)
    "udp://bt1.archive.org:6969/announce",
    "udp://bt2.archive.org:6969/announce",
    
    # Tier 5: Trackers extras de alta qualidade
    "udp://tracker.filemail.com:6969/announce",
    "udp://tracker1.bt.moack.co.kr:80/announce",
    "udp://9.rarbg.com:2810/announce",
    "udp://tracker.uw0.xyz:6969/announce",
    "udp://tracker.dler.org:6969/announce",
    "udp://tracker.lelux.fi:6969/announce",
    "udp://movies.zsw.ca:6969/announce",
    "udp://tracker1.myporn.club:9337/announce",
    "udp://open.tracker.cl:1337/announce",
    "udp://tracker.dump.cl:6969/announce",
    "udp://tracker.auctor.tv:6969/announce",
    "udp://tracker.srv00.com:6969/announce",
    "udp://tracker.doko.moe:6969/announce",
    "udp://tracker.qu.ax:6969/announce",
    "udp://tracker.swateam.org.uk:2710/announce",
]


def find_aria2_binary(project_root: Optional[str] = None) -> Optional[str]:
    """Return path to aria2c binary.

    Search order:
    1. Environment variable ARIA2C_PATH
    2. Provided project_root for aria2c.exe or aria2c
    3. PATH (shutil.which)
    """
    # 1. env var
    env_path = os.environ.get("ARIA2C_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. project root (common files: aria2c.exe or aria2c)
    if project_root:
        # check common direct locations
        candidate = os.path.join(project_root, "aria2c.exe") if sys.platform == "win32" else os.path.join(project_root, "aria2c")
        if os.path.exists(candidate):
            return candidate
        alt = os.path.join(project_root, "aria2c")
        if os.path.exists(alt):
            return alt

        # search a bit deeper: look for aria2c inside immediate subfolders (depth 2)
        try:
            for root, dirs, files in os.walk(project_root):
                # limit depth to avoid long scans: allow project_root and one level below
                rel = os.path.relpath(root, project_root)
                if rel != '.' and rel.count(os.sep) >= 2:
                    # skip deeper
                    continue
                for fname in files:
                    if fname.lower() in ("aria2c.exe", "aria2c"):
                        candidate_path = os.path.join(root, fname)
                        if os.path.exists(candidate_path):
                            return candidate_path
        except Exception:
            pass

    # 3. PATH
    path = shutil.which("aria2c")
    return path


async def download_magnet_cli(magnet_url: str, dest_path: str, progress_cb: Optional[callable] = None, stop_event: Optional[asyncio.Event] = None, aria2_path: Optional[str] = None, project_root: Optional[str] = None, total_size_hint: Optional[int] = None, job_id: Optional[int] = None, job_manager: Optional[object] = None) -> tuple[str, str]:
    """
    Download magnet using aria2c CLI (like v0).
    Monitors file size while aria2 is running with robust progress detection.
    
    Args:
        magnet_url: Magnet link URL
        dest_path: Destination path
        progress_cb: Callback for progress updates
        stop_event: Event to signal download stop
        aria2_path: Path to aria2c binary
        project_root: Project root for finding aria2c
        total_size_hint: Known total size (from item metadata) to use instead of estimating
        job_id: Job ID for tracking cancel vs pause state
        job_manager: JobManager instance for checking cancel status
    
    Returns:
        Tuple of (download_path, status) where status is "completed", "paused", or "canceled"
    
    Returns the final destination path.
    """
    if not aria2_path:
        aria2_path = find_aria2_binary(project_root)
    
    if not aria2_path or not os.path.exists(aria2_path):
        raise FileNotFoundError("aria2c binary not found")
    
    dest = Path(dest_path)
    
    # Sanitize filename to avoid Windows invalid characters
    def sanitize_filename(filename: str) -> str:
        """Remove invalid characters from filename for Windows"""
        invalid_chars = '\\/:*?"<>|'
        sanitized = ''.join((c if c not in invalid_chars else '_') for c in filename)
        sanitized = sanitized.strip()
        if sanitized in ('.', '..'):
            sanitized = '_' + sanitized
        return sanitized or 'download'
    
    safe_name = sanitize_filename(dest.name)
    if safe_name != dest.name:
        print(f"Sanitizing filename: '{dest.name}' -> '{safe_name}'")
        dest = dest.parent / safe_name
    
    # Create parent directory
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    # ==================== SESSION MANAGEMENT ====================
    # CRITICAL: Session handling MUST be done BEFORE any directory manipulation
    # This preserves aria2's .aria2 metadata and GID references
    
    session_file, dht_file = _get_aria2_paths()
    load_session = False
    saved_gid = None  # Will be loaded from session if resuming
    
    # Check if session file exists
    if session_file.exists():
        try:
            session_size = session_file.stat().st_size
            if session_size < 100:  # Session file should be at least a few KB
                print(f"Session file too small ({session_size} bytes), will start fresh")
                session_file.unlink()
            else:
                # Check if the session file contains the SAME magnet URL
                session_content = session_file.read_text()
                if magnet_url in session_content:
                    # Same magnet - this is a RESUME
                    load_session = True
                    print(f"Session matches magnet URL - RESUMING")
                else:
                    # Different magnet - delete old session and start fresh
                    print(f"Different magnet detected - removing old session")
                    try:
                        session_file.unlink()
                    except Exception as e:
                        print(f"Could not delete session: {e}")
        except Exception as e:
            print(f"Could not validate session file: {e}, will start fresh")
    
    if load_session:
        print(f"===== RESUMING FROM SESSION =====")
        print(f"Session file size: {session_file.stat().st_size} bytes")
        print(f"NO directory manipulation will occur")
        print(f"aria2 will use existing .aria2 metadata and preserve state")
        print(f"================================")
        
        # When resuming: FIND THE ACTUAL FOLDER that aria2 created (has .aria2 metadata)
        # This is CRITICAL - we must use the EXACT folder name that aria2 is using
        actual_download_folder = None
        saved_gid = None
        
        # PRIORITY 1: Find folder with .aria2 metadata (this is where aria2 is actually downloading to)
        try:
            parent = dest.parent
            if parent.exists():
                for item in sorted(parent.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
                    if item.is_dir():
                        aria2_meta = Path(str(item) + ".aria2")
                        if aria2_meta.exists():
                            actual_download_folder = item
                            print(f"Found actual download folder with .aria2 metadata: {item.name}")
                            break
        except Exception as e:
            print(f"Could not find actual folder: {e}")
        
        # Read session to get the GID - this might be metadata GID, we'll update it later with real GID
        try:
            with open(session_file, 'r') as f:
                for line in f:
                    if line.strip().startswith('gid='):
                        saved_gid = line.strip().replace('gid=', '', 1)
                        print(f"Found saved GID from session: {saved_gid} (may be metadata GID)")
                        print(f"   Note: Real GID will be captured when download starts")
                        break
        except Exception as e:
            print(f"Could not read session: {e}")
        
        # CRITICAL: Use the ACTUAL folder name that aria2 created, not the sanitized name
        if actual_download_folder:
            # Use the folder that has the .aria2 metadata - this is where aria2 is resuming from
            dest = dest.parent / actual_download_folder.name
            print(f"RESUME: Using actual folder --out={actual_download_folder.name}")
        # Note: If no .aria2 found, aria2 will still resume from aria2.session file
        # So this is not a fatal condition
    else:
        # ONLY cleanup if starting fresh (not resuming)
        print(f"===== STARTING FRESH DOWNLOAD =====")
        print(f"Cleaning up any previous files")
        print(f"===================================")
        try:
            # Remove metadata attached to dest path
            aria2_meta = Path(str(dest) + ".aria2")
            aria2_temp = Path(str(dest) + ".aria2c")
            
            if aria2_meta.exists():
                try:
                    aria2_meta.unlink()
                    print(f"Removed previous .aria2 metadata")
                except Exception as e:
                    print(f"Could not remove .aria2 metadata: {e}")
            
            if aria2_temp.exists():
                try:
                    aria2_temp.unlink()
                    print(f"Removed previous .aria2c metadata")
                except Exception as e:
                    print(f"Could not remove .aria2c metadata: {e}")
            
            # Remove destination folder only if starting fresh
            if dest.is_dir():
                try:
                    shutil.rmtree(dest)
                    print(f"Removed previous directory: {dest}")
                except Exception as e:
                    print(f"Could not remove directory: {e}")
            elif dest.exists():
                try:
                    dest.unlink()
                    print(f"Removed previous file: {dest}")
                except Exception as e:
                    print(f"Could not remove file: {e}")
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
    
    # NOTE: Do NOT create dest folder beforehand!
    # aria2 will create the folder structure automatically when it starts downloading
    # Creating it empty beforehand causes: empty folder creation + stray .torrent files
    # Let aria2 handle the folder creation naturally
    
    # Build aria2 command (CLI mode, no RPC)
    # CRITICAL: When resuming, ONLY use --input-file, do NOT pass magnet URL again
    
    if load_session:
        #  RESUME: Minimal command - let aria2 load everything from session
        # DO NOT include magnet URL - that would create a NEW download with NEW GID
        print(f"RESUME MODE: Using ONLY --input-file={session_file}")
        print(f"   aria2 will load GID, folder name, and all parameters from session")
        print(f"   Using --force-save=true to ensure session is updated with real GID")
        cmd = [
            aria2_path,
            '--enable-rpc=false',
            '--continue=true',
            '--auto-file-renaming=false',
            '--reuse-uri=true',
            '--allow-overwrite=true',
            '--max-resume-failure-tries=10',
            '--force-save=true',
            '--save-session=' + str(session_file),
            '--save-session-interval=1',
            '--bt-save-metadata=true',
            '--bt-metadata-only=false',
            '--bt-load-saved-metadata=true',
            '--bt-detach-seed-only=false',  # NUNCA desconectar de seeders!
            '--file-allocation=none',
            '--seed-time=0',
            '--bt-max-peers=1000',
            '--bt-max-open-files=1024',
            '--max-connection-per-server=16',
            '--max-concurrent-downloads=1',
            '--check-integrity=false',
            '--log-level=debug',
            '--bt-tracker-connect-timeout=10',
            '--bt-tracker-interval=15',  # Atualiza a cada 15s (mais agressivo)
            '--dht-listen-port=6881-6889',
            '--enable-dht=true',
            '--enable-dht6=true',  # IPv6 DHT ativado para mais seeders
            '--bt-enable-lpd=true',
            '--dht-file-path=' + str(dht_file),
            '--summary-interval=1',
            '--max-tries=5',
            '--retry-wait=1',
            # === OTIMIZAÇÕES SEGURAS (adicionadas) ===
            '--use-head=false',
            '--allow-piece-length-change=true',
            '--max-upload-limit=300K',
            '--bt-request-peer-speed-limit=0',
            '--connect-timeout=15',
            '--min-split-size=1M',
            '--bt-request-peer-speed=1',
            '--input-file=' + str(session_file)
        ]
        print(f" Session loaded - continuing download with existing GID and folder")
    else:
        #  FRESH START: Full command with magnet URL and all parameters
        print(f"FRESH START: Creating new download session")
        print(f"   Using --force-save=true to ensure real GID is captured when metadata finishes")
        cmd = [
            aria2_path,
            '--enable-rpc=false',
            '--dir=' + str(dest.parent),
            '--out=' + dest.name,
            '--continue=true',
            '--auto-file-renaming=false',
            '--reuse-uri=true',
            '--allow-overwrite=true',
            '--max-resume-failure-tries=10',
            '--force-save=true',
            '--save-session=' + str(session_file),
            '--save-session-interval=1',
            '--bt-save-metadata=true',
            '--bt-metadata-only=false',
            '--bt-load-saved-metadata=true',
            '--bt-detach-seed-only=false',  # NUNCA desconectar de seeders!
            '--file-allocation=none',
            '--seed-time=0',
            '--bt-max-peers=0',  # Sem limite de peers
            '--bt-max-open-files=4096',  # Mais conexões simultâneas para seeders
            '--max-connection-per-server=16',
            '--max-concurrent-downloads=1',
            '--check-integrity=false',
            '--log-level=debug',
            '--bt-tracker-connect-timeout=3',  # Timeout 3s (mais agressivo)
            '--bt-tracker-interval=15',  # Atualiza a cada 15s (mais agressivo para seeders)
            '--dht-listen-port=6881-6889',
            '--dht-entry-point=dht.transmissionbt.com:6881',  # DHT bootstrap para descoberta rápida
            '--dht-entry-point6=dht.transmissionbt.com:6881',  # DHT bootstrap IPv6
            '--enable-dht=true',
            '--enable-dht6=true',  # IPv6 DHT ativado para mais seeders
            '--bt-enable-lpd=true',
            '--dht-file-path=' + str(dht_file),
            '--summary-interval=1',
            '--max-tries=5',
            '--retry-wait=1',
            # === OTIMIZAÇÕES AGRESSIVAS PARA MÁXIMA PERFORMANCE ===
            '--use-head=false',
            '--allow-piece-length-change=true',
            '--max-upload-limit=0',  # SEM LIMITE de upload (era 300K)
            '--bt-request-peer-speed-limit=0',
            '--connect-timeout=5',  # Reduzido de 15 para 5 (conecta mais rápido)
            '--min-split-size=1M',
            '--bt-request-peer-speed=1',
            '--peer-id-prefix=-qB4390-',  # Simula qBittorrent para melhor aceitação
            '--user-agent=qBittorrent/4.5.0',  # User agent qBittorrent (versão mais recente)
            '--listen-port=6881-6889',  # Porta de escuta para conexões incoming
            '--enable-peer-exchange=true',  # PEX para descobrir mais peers
            '--bt-seed-unverified=true',  # Permite seed de peças não verificadas (mais rápido)
            '--bt-hash-check-seed=false',  # Não verifica hash ao retomar (mais rápido)
            '--bt-prioritize-piece=head=16M,tail=16M',  # Prioriza início e fim (streaming)
        ]
        
        # Injetar trackers extras para maximizar peers/seeders
        # Formato: --bt-tracker=tracker1,tracker2,tracker3
        if TRACKERS_EXTRAS:
            trackers_str = ','.join(TRACKERS_EXTRAS)
            cmd.append(f'--bt-tracker={trackers_str}')
            print(f" TRACKERS EXTRAS INJETADOS: {len(TRACKERS_EXTRAS)} trackers adicionados")
        
        print(f" FRESH START: Session will be created new with SAFE optimizations")
        # Add magnet URL ONLY for fresh start
        cmd.append(magnet_url)
    
    print(f"Starting aria2: {aria2_path}")
    print(f"Destination: {dest}")
    print(f"Command: {' '.join(cmd)}")
    
    # Start aria2 process with PIPE for both stdout and stderr
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout for better debugging
        universal_newlines=True,
        bufsize=1,  # Line buffered
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
    )
    
    print(f"aria2c PID: {proc.pid}")
    
    # Initialize state tracking
    process_start_time = time.time()
    detection_window = 60
    last_size_bytes = 0
    total_size_bytes = 0
    total_size_detected = False
    detected_candidate = None
    final_download_path = None  # Track the actual path where files were downloaded
    last_progress_update_time = time.time()
    last_reported_size = 0
    
    # GID Tracking: Detect and capture the REAL download GID (not metadata GID)
    metadata_gid = saved_gid[:6] if saved_gid else None  # Normalize to 6-char short form
    real_gid = None  # The actual download GID (different from metadata)
    real_gid_detected = False
    gid_detection_start = time.time()
    
    # Thread-safe log buffer
    aria2_log_buffer = []
    log_lock = threading.Lock()
    
    def read_aria2_output():
        """Read aria2 output line by line and buffer it"""
        try:
            for line in iter(proc.stdout.readline, ''):
                if line:
                    line = line.rstrip('\n')
                    if line:
                        print(f"   [aria2] {line}")
                        with log_lock:
                            aria2_log_buffer.append(line)
        except Exception as e:
            print(f"Error reading aria2 output: {e}")
    
    log_thread = threading.Thread(target=read_aria2_output, daemon=True)
    log_thread.start()
    
    # Track if aria2 loaded existing session
    session_loaded_indicator = False
    
    # Track last reported values to avoid duplicate logs
    last_reported_speed = 0
    last_reported_progress_pct = 0
    
    def extract_download_path_from_logs() -> Optional[Path]:
        """
        Parse aria2 logs to find actual download path.
        Looks for lines like: FILE: C:/Users/diego/Downloads/Hollow Knight.../fg-01.bin
        Extracts the folder path (without the filename).
        """
        try:
            with log_lock:
                if not aria2_log_buffer:
                    return None
                
                # Search from most recent to oldest
                recent_lines = aria2_log_buffer[-50:] if len(aria2_log_buffer) > 50 else aria2_log_buffer
                
                for log_line in reversed(recent_lines):
                    # Look for FILE: patterns in logs
                    if "FILE:" in log_line:
                        # Extract path from FILE: to the last /filename
                        # Use greedy .+ to capture the full path, then strip the last component
                        match = re.search(r'FILE:\s*(.+)/[^/]+(?:\s|$)', log_line)
                        if match:
                            path_str = match.group(1).strip()
                            # Convert forward slashes to backslashes for Windows
                            path_str = path_str.replace('/', '\\')
                            candidate = Path(path_str)
                            # Verify the directory exists
                            if candidate.exists():
                                return candidate
        except Exception:
            pass
        return None
    
    # ==================== HELPER FUNCTIONS ====================
    
    def extract_gid_from_log_line(log_line: str) -> Optional[str]:
        """
        Extract GID from aria2 log lines like:
        [#401b0b 0B/4.7KiB(0%)...]     <- metadata GID (short form)
        [#967bda 0B/851MiB(0%)...]     <- real download GID (short form)
        [#be0a87d67f9e2e3d 0B/...]     <- full GID form
        
        The real GID is usually a different one that appears later,
        when actual bytes are being downloaded (not metadata).
        Returns the short 6-character form for comparison.
        """
        try:
            # Try to match full GID first: [#XXXXXXXXXXXXXXXX or [#XXXXXX
            match = re.search(r'\[#([a-f0-9]{6,})', log_line)
            if match:
                full_gid = match.group(1)
                # Return short form (first 6 chars) for consistent comparison
                return full_gid[:6]
        except Exception:
            pass
        return None
    
    def update_session_with_real_gid(real_gid: str) -> bool:
        """
        Update aria2.session file to contain the REAL download GID.
        This is called when we detect a new GID appearing in logs.
        
        Replaces the old metadata GID with the new real GID in aria2.session.
        The real_gid comes as a 6-char short form from logs.
        
        Returns True if successfully updated.
        """
        try:
            if not session_file.exists():
                print(f"Session file not found, cannot update GID")
                return False
            
            # Read current session
            content = session_file.read_text()
            
            # Find ALL gid= lines (there may be multiple entries)
            # Pattern: gid=XXXXXXXXXXXXXXXX (16 chars) or gid=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX (32 chars)
            # aria2 uses 16-char GIDs in session files
            gid_matches = list(re.finditer(r'gid=([a-f0-9]{16}|[a-f0-9]{32})', content))
            
            if not gid_matches:
                print(f"No GID found in session file (searched for 16 or 32-char formats)")
                return False
            
            # Update ALL GID entries that match the old short form
            updated_content = content
            updated_count = 0
            
            for match in gid_matches:
                old_full_gid = match.group(1)
                old_short_gid = old_full_gid[:6]
                
                # Only update if we found a different GID
                if old_short_gid != real_gid:
                    # Construct new full GID
                    new_full_gid = real_gid + old_full_gid[6:]
                    
                    print(f"Updating session GID from {old_short_gid} to {real_gid}")
                    print(f"   Old full GID: {old_full_gid}")
                    print(f"   New full GID: {new_full_gid}")
                    
                    # Replace this specific GID
                    updated_content = updated_content.replace(
                        f'gid={old_full_gid}', 
                        f'gid={new_full_gid}',
                        1  # Replace only first occurrence per loop iteration
                    )
                    updated_count += 1
            
            if updated_count == 0:
                print(f"Session already has correct GID")
                return True
            
            # Write back to file IMMEDIATELY
            session_file.write_text(updated_content)
            
            print(f" Session file UPDATED - {updated_count} GID(s) changed from metadata to real")
            print(f"   File saved: {session_file}")
            
            # Verify the write was successful
            verify_content = session_file.read_text()
            if real_gid in verify_content:
                print(f"Verification: New GID {real_gid} confirmed in session file")
                return True
            else:
                print(f"Verification FAILED: New GID not found in session after write!")
                return False
            
        except Exception as e:
            print(f"Error updating session GID: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
    # ==================== MAIN HELPER FUNCTIONS ====================
    
    def parse_aria2_progress(log_line: str) -> Optional[Dict[str, Any]]:
        """
        Parse aria2 progress line like:
        [#2d5f00 0B/8.7KiB(0%) CN:51 SD:3 DL:0B]
        [#69e19f 344MiB/1.6GiB(20%) CN:72 SD:12 DL:11MiB ETA:1m51s]
        
        Returns dict with keys: downloaded_bytes, total_bytes, percentage, peers, seeders, speed_bytes_per_sec
        """
        try:
            # Match pattern: [#HASH DOWNLOADED/TOTAL(%)...]
            match = re.search(r'\[#[a-f0-9]+ ([\d.]+)(B|KiB|MiB|GiB)/([\d.]+)(B|KiB|MiB|GiB)', log_line)
            if match:
                down_val, down_unit, total_val, total_unit = match.groups()
                
                multipliers = {'B': 1, 'KiB': 1024, 'MiB': 1024**2, 'GiB': 1024**3}
                
                downloaded_bytes = int(float(down_val) * multipliers.get(down_unit, 1))
                total_bytes = int(float(total_val) * multipliers.get(total_unit, 1))
                
                # Extract percentage
                pct_match = re.search(r'\((\d+)%\)', log_line)
                percentage = int(pct_match.group(1)) if pct_match else 0
                
                # Extract peers/seeders
                peers_match = re.search(r'CN:(\d+)', log_line)
                peers = int(peers_match.group(1)) if peers_match else 0
                
                seeders_match = re.search(r'SD:(\d+)', log_line)
                seeders = int(seeders_match.group(1)) if seeders_match else 0
                
                # Extract speed (DL:VALUE)
                speed_bytes_per_sec = 0
                speed_match = re.search(r'DL:([\d.]+)(B|KiB|MiB|GiB)', log_line)
                if speed_match:
                    speed_val, speed_unit = speed_match.groups()
                    speed_bytes_per_sec = int(float(speed_val) * multipliers.get(speed_unit, 1))
                
                return {
                    'downloaded': downloaded_bytes,
                    'total': total_bytes,
                    'percentage': percentage,
                    'peers': peers,
                    'seeders': seeders,
                    'speed': speed_bytes_per_sec
                }
        except Exception:
            pass
        return None
    
    def get_latest_progress_from_logs() -> Optional[Dict[str, Any]]:
        """Extract latest progress information from log buffer"""
        with log_lock:
            if not aria2_log_buffer:
                return None
            
            # Search from most recent to oldest
            recent_lines = aria2_log_buffer[-200:] if len(aria2_log_buffer) > 200 else aria2_log_buffer
            
            for log_line in reversed(recent_lines):
                result = parse_aria2_progress(log_line)
                if result:
                    return result
        return None
    
    def sum_directory_size(directory: Path) -> int:
        """Recursively sum all file sizes in directory, return 0 if any error"""
        try:
            total = 0
            for item in directory.rglob('*'):
                if item.is_file():
                    try:
                        total += item.stat().st_size
                    except Exception:
                        pass
            return total
        except Exception:
            return 0
    
    def detect_aria2_created_path() -> Optional[Path]:
        """
        Aria2 may create files/folders with different names than expected.
        Detect files created recently by aria2 process.
        """
        try:
            candidates = []
            for p in dest.parent.iterdir():
                # Skip metadata files
                if p.name.endswith(('.aria2', '.aria2c', '.torrent')):
                    continue
                
                try:
                    p_ctime = p.stat().st_ctime
                    p_mtime = p.stat().st_mtime
                    current_time = time.time()
                    
                    # Check if file was modified within process window
                    if (current_time - p_ctime) < (detection_window + 5) or (current_time - p_mtime) < (detection_window + 5):
                        candidates.append(p)
                except Exception:
                    pass
            
            if candidates:
                # Prefer larger items (more likely to be actual download, not temp)
                def get_item_size(p):
                    if p.is_file():
                        try:
                            return p.stat().st_size
                        except:
                            return 0
                    elif p.is_dir():
                        return sum_directory_size(p)
                    return 0
                
                candidates.sort(key=get_item_size, reverse=True)
                return candidates[0]
        except Exception:
            pass
        return None
    
    def try_get_total_size_from_metadata() -> int:
        """Try to read total size from .aria2 or .aria2c metadata files"""
        try:
            for meta_suffix in ['.aria2', '.aria2c']:
                meta_file = Path(str(dest) + meta_suffix)
                if meta_file.exists():
                    try:
                        tree = ET.parse(meta_file)
                        root = tree.getroot()
                        
                        # For torrents, sum all file lengths
                        total_from_meta = 0
                        file_count = 0
                        for file_elem in root.findall('.//file'):
                            try:
                                length_str = file_elem.get('length')
                                if length_str:
                                    total_from_meta += int(length_str)
                                    file_count += 1
                            except:
                                pass
                        
                        if total_from_meta > 0:
                            print(f"Detected total size from {meta_suffix} metadata: {total_from_meta / 1024 / 1024 / 1024:.2f}GB ({file_count} files)")
                            return total_from_meta
                    except Exception:
                        pass
        except Exception:
            pass
        return 0
    
    def try_extract_total_from_logs() -> int:
        """Try to extract total size from recent log lines"""
        try:
            progress = get_latest_progress_from_logs()
            if progress and progress.get('total', 0) > 0:
                return progress['total']
        except Exception:
            pass
        return 0
    
    def estimate_total_size(current: int) -> int:
        """Estimate total size based on current size"""
        if current > 0:
            # Conservative estimate: assume we're at most at 33% completion
            estimated = int(current * 3.0)
            print(f" Estimating total size: {estimated / 1024 / 1024 / 1024:.2f}GB (based on current {current / 1024 / 1024 / 1024:.2f}GB)")
            return estimated
        return 0
    
    # ==================== MAIN LOOP ====================

    try:
        while proc.poll() is None:
            # -------------------- STOP / PAUSE --------------------
            if stop_event and stop_event.is_set():
                try:
                    proc.terminate()  # Graceful shutdown
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                except Exception as e:
                    print(f"Error sending pause signal: {e}")
                break

            # -------------------- REAL GID DETECTION --------------------
            if metadata_gid is None:
                with log_lock:
                    recent_lines = aria2_log_buffer[-200:]
                for log_line in recent_lines:
                    found_gid = extract_gid_from_log_line(log_line)
                    if found_gid:
                        metadata_gid = found_gid
                        print(f"Established metadata GID from logs: {metadata_gid}")
                        break

            if not real_gid_detected and metadata_gid:
                with log_lock:
                    recent_lines = aria2_log_buffer[-200:]
                for log_line in recent_lines:
                    found_gid = extract_gid_from_log_line(log_line)
                    if found_gid and found_gid != metadata_gid:
                        real_gid = found_gid
                        real_gid_detected = True
                        print(f"DETECTED REAL GID: {real_gid} (metadata was: {metadata_gid})")
                        # CRITICAL: Reset speed calculation when GID changes
                        last_reported_size = 0
                        last_report_time = time.time()
                        print(f"   Speed calculation reset for new GID")
                        if update_session_with_real_gid(real_gid):
                            print(f" Session saved with REAL GID: {real_gid}")
                            if job_manager and job_id:
                                try:
                                    print(f"   Next resume will use this REAL GID: {real_gid}")
                                except Exception:
                                    pass
                        break

            # -------------------- PROGRESS / SIZE --------------------
            progress_data = get_latest_progress_from_logs()
            current_size_bytes = 0

            if progress_data:
                current_size_bytes = progress_data['downloaded']
                if not session_loaded_indicator and load_session and current_size_bytes > 0:
                    session_loaded_indicator = True
                    print(f" Session loaded! aria2 is continuing download ({current_size_bytes} bytes detected)")
                if not final_download_path:
                    actual_path = extract_download_path_from_logs()
                    final_download_path = actual_path or (dest if dest.exists() else None)
                # Disk checks previously caused progress jumps on sparse files (e.g. with tail prioritization).
                # We trust Aria2 logs for progress data.
                pass
            else:
                if dest.exists():
                    current_size_bytes = sum_directory_size(dest) if dest.is_dir() else dest.stat().st_size
                    if current_size_bytes > 0 and not final_download_path:
                        final_download_path = dest
                else:
                    alt_path = detect_aria2_created_path()
                    if alt_path:
                        current_size_bytes = sum_directory_size(alt_path) if alt_path.is_dir() else alt_path.stat().st_size
                        detected_candidate = alt_path
                        final_download_path = alt_path

            # -------------------- TOTAL SIZE DETECTION --------------------
            if not total_size_detected:
                total_size_bytes = try_get_total_size_from_metadata() or try_extract_total_from_logs() or total_size_hint
                if not total_size_bytes and current_size_bytes > 1_000_000:
                    total_size_bytes = estimate_total_size(current_size_bytes)
                total_size_detected = total_size_bytes > 0
            else:
                log_size = try_extract_total_from_logs()
                if log_size > total_size_bytes:
                    total_size_bytes = log_size
                    print(f"Refined total size from logs: {total_size_bytes / 1024 / 1024 / 1024:.2f}GB")

            # -------------------- PROGRESS CALCULATION --------------------
            # PRIORITY: Use Aria2's reported percentage if available (avoids rounding errors from "0.9GiB" logs)
            potential_pct = 0.0
            if progress_data and 'percentage' in progress_data:
                potential_pct = progress_data['percentage'] / 100.0
            
            # Calculate computed percentage from bytes
            computed_pct = min(current_size_bytes / total_size_bytes, 0.99) if total_size_bytes else 0.0
            
            # Use the higher of the two to avoid regressions, but prefer Aria2's explicit % for precision
            # (e.g., Aria2 says 99% but bytes say 0.9GB which is 90%)
            if potential_pct > computed_pct:
                progress_pct = potential_pct
                # Refine current_size_bytes to match the progress percentage if we have a valid total
                # This fixes the "stuck at 90%" issue when log shows "0.9GiB" (rounded) but progress is 99%
                if total_size_bytes and progress_pct > 0:
                    refined_current = int(total_size_bytes * progress_pct)
                    if refined_current > current_size_bytes:
                        current_size_bytes = refined_current
            else:
                progress_pct = computed_pct
            time_since_last_report = time.time() - last_progress_update_time

            size_changed = abs(current_size_bytes - last_reported_size) > 1_000_000
            
            # CRITICAL: Always use aria2's reported speed when available (it's accurate!)
            # Only fallback to manual calculation when aria2 doesn't report speed
            if progress_data and progress_data.get('speed', 0) > 0:
                # Use aria2's speed (most accurate)
                speed_mb_per_sec = progress_data['speed'] / 1024 / 1024
            elif time_since_last_report > 0.1 and current_size_bytes > last_reported_size and last_reported_size > 0:
                # Fallback: calculate from delta bytes / delta time
                calculated_speed = ((current_size_bytes - last_reported_size) / time_since_last_report) / 1024 / 1024
                
                # If speed > 500MB/s (4Gbps), it's likely disk I/O (resume check), not download speed.
                # Clamp it to last known speed or 0 to avoid UI spikes.
                if calculated_speed > 500:
                    speed_mb_per_sec = last_reported_speed
                else:
                    speed_mb_per_sec = calculated_speed
            else:
                # No data available or first iteration - use last known speed or 0
                speed_mb_per_sec = last_reported_speed if last_reported_speed > 0 else 0.0
                # Initialize last_reported_size on first iteration to prevent absurd calculations
                if last_reported_size == 0 and current_size_bytes > 0:
                    last_reported_size = current_size_bytes
            
            speed_changed = abs(speed_mb_per_sec - last_reported_speed) > 0.2
            progress_changed = abs(progress_pct * 100 - last_reported_progress_pct) > 0.1
            should_report = size_changed or speed_changed or progress_changed or time_since_last_report > 0.5

            if should_report:
                activity = current_size_bytes > last_size_bytes
                last_size_bytes = current_size_bytes if activity else last_size_bytes
                last_progress_update_time = time.time()
                if progress_data:
                    print(f"Progress: {progress_pct*100:.1f}% ({current_size_bytes/1024/1024/1024:.2f}GB) "
                        f"speed={speed_mb_per_sec:.2f}MB/s peers={progress_data.get('peers', 0)} "
                        f"seeders={progress_data.get('seeders', 0)}")
                else:
                    print(f"Progress: {progress_pct*100:.1f}% ({current_size_bytes/1024/1024/1024:.2f}GB) "
                        f"speed={speed_mb_per_sec:.2f}MB/s")
                if progress_cb:
                    await progress_cb(current_size_bytes, total_size_bytes if total_size_detected else None,
                                    peers=progress_data.get('peers', 0) if progress_data else 0,
                                    seeders=progress_data.get('seeders', 0) if progress_data else 0,
                                    speed=int(speed_mb_per_sec * 1024 * 1024))
                last_reported_size = current_size_bytes
                last_reported_speed = speed_mb_per_sec
                last_reported_progress_pct = progress_pct * 100

            # -------------------- TIMEOUT LOGIC --------------------
            time_since_last_progress = time.time() - last_progress_update_time
            if current_size_bytes == 0:
                timeout_threshold = 180
            elif current_size_bytes < 1_000_000:
                timeout_threshold = 300
            elif current_size_bytes < 100_000_000:
                timeout_threshold = 600
            else:
                timeout_threshold = 600

            # CRITICAL: Detect near-complete torrents stuck at 98%+
            # If download is 98%+ complete and hasn't progressed in 2 minutes, consider it done
            if total_size_detected and total_size_bytes > 0:
                progress_pct = current_size_bytes / total_size_bytes
                if progress_pct >= 0.98 and time_since_last_progress > 120:
                    print(f"Download is {progress_pct*100:.1f}% complete and stalled for {time_since_last_progress:.0f}s")
                    print(f"   Downloaded: {current_size_bytes / (1024**3):.2f} GB / {total_size_bytes / (1024**3):.2f} GB")
                    print(f"   Considering download as COMPLETE (missing pieces likely unavailable)")
                    proc.kill()
                    # Force completion by breaking the loop
                    break

            if time_since_last_progress > timeout_threshold:
                print(f"TIMEOUT: No progress for {time_since_last_progress:.0f}s (threshold={timeout_threshold}s)")
                if progress_data:
                    print(f"   Last known: peers={progress_data.get('peers', 0)}, seeders={progress_data.get('seeders', 0)}")
                proc.kill()
                raise RuntimeError(f"No progress for {time_since_last_progress:.0f}s - download stalled")

            if (time.time() - process_start_time) > 7200 and current_size_bytes == 0:
                print(f"Download exceeded 2 hours with no progress, killing aria2")
                proc.kill()
                raise RuntimeError("Download exceeded 2 hours with no progress")

            await asyncio.sleep(0.1)

    finally:
        # -------------------- FINALIZATION --------------------
        paused = stop_event and stop_event.is_set()
        job_paused = job_id and job_manager and job_manager.is_job_paused(job_id)
        canceled = job_id and job_manager and job_manager.is_job_canceled(job_id)

        if proc.returncode == 0 and not paused:
            final_status = "completed"
        elif job_paused:
            final_status = "paused"
        elif canceled:
            final_status = "canceled"
        else:
            final_status = "paused" if paused else "canceled"

        if job_paused:
            print(f"Download PAUSED - preserving metadata for resume")
            try:
                actual_dest = final_download_path or detected_candidate or dest
                if actual_dest and Path(actual_dest).exists() and Path(actual_dest).is_dir():
                    aria2_meta_inside = actual_dest / '.aria2'
                    aria2_meta_outside = Path(str(actual_dest) + '.aria2')
                    if aria2_meta_inside.exists() and not aria2_meta_outside.exists():
                        try:
                            aria2_meta_inside.rename(aria2_meta_outside)
                        except Exception:
                            import shutil
                            shutil.move(str(aria2_meta_inside), str(aria2_meta_outside))
                    elif aria2_meta_inside.exists() and aria2_meta_outside.exists():
                        aria2_meta_inside.unlink()
            except Exception as e:
                print(f"Error managing .aria2 metadata: {e}")
        elif canceled:
            print(f"Download CANCELED - cleaning up files and metadata")
            try:
                session_file, _ = _get_aria2_paths()
                if session_file.exists():
                    session_file.unlink()
            except Exception as e:
                print(f"Could not remove aria2.session: {e}")
        else:
            try:
                for pattern in ['.aria2', '.aria2c']:
                    meta_file = Path(str(dest) + pattern)
                    if meta_file.exists():
                        meta_file.unlink()
                for item in dest.parent.glob('*.torrent'):
                    item.unlink()
            except Exception:
                pass

        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        with log_lock:
            if aria2_log_buffer:
                print(f"aria2 produced {len(aria2_log_buffer)} log lines")

    paused = stop_event and stop_event.is_set()
    if proc.returncode not in (0, None) and not paused:
        error_msg = f"aria2 exit code: {proc.returncode}"
        print(f"aria2 failed: {error_msg}")
        raise RuntimeError(error_msg)

    # -------------------- RETURN FINAL PATH --------------------
    if final_download_path:
        print(f"{'Download paused' if paused else 'Download completed'} at: {final_download_path}")
        return str(final_download_path), final_status
    elif detected_candidate and detected_candidate.exists():
        print(f"{'Download paused' if paused else 'Download completed'} at: {detected_candidate}")
        return str(detected_candidate), final_status
    elif dest.exists():
        print(f"{'Download paused' if paused else 'Download completed'} at: {dest}")
        return str(dest), final_status
    else:
        raise RuntimeError("Download completed but destination files not found")
