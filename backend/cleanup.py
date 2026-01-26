import os
import time
from pathlib import Path
from typing import List

def cleanup_old_logs(max_days: int = 7) -> None:
    """
    Remove logs older than `max_days` from the logs directory.
    Uses APP_DATA_DIR / logs.
    """
    try:
        app_data = os.environ.get("APP_DATA_DIR")
        if not app_data:
            # Fallback based on typical structure if env var not set
            local_app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") 
            if local_app_data:
                app_data = os.path.join(local_app_data, "furious-app")
            else:
                return

        logs_dir = Path(app_data) / "logs"
        
        if not logs_dir.exists():
            return

        now = time.time()
        cutoff = now - (max_days * 86400)
        
        count = 0
        deleted_size = 0

        # List of log patterns to clean
        patterns = ["*.log", "*.log.*"]

        for pattern in patterns:
            for log_file in logs_dir.glob(pattern):
                try:
                    stats = log_file.stat()
                    if stats.st_mtime < cutoff:
                        size = stats.st_size
                        os.remove(log_file)
                        count += 1
                        deleted_size += size
                except Exception as e:
                    print(f"[Cleanup] Failed to delete {log_file}: {e}")
        
        if count > 0:
            human_size = f"{deleted_size / 1024:.1f}KB"
            if deleted_size > 1024*1024:
                human_size = f"{deleted_size / (1024*1024):.1f}MB"
            print(f"[Cleanup] Removed {count} old log files ({human_size})")

    except Exception as e:
        print(f"[Cleanup] Error during log cleanup: {e}")
