import os

# Optional environment variable to point to aria2 binary
ARIA2C_PATH = os.environ.get("ARIA2C_PATH")

_app_data_dir = os.environ.get("APP_DATA_DIR")

# Default download dir: prefer the user's Downloads folder when available
_env_dl = os.environ.get("DOWNLOADS_DIR")
if _env_dl:
	DOWNLOADS_DIR = _env_dl
else:
	home = os.path.expanduser("~") or os.getcwd()
	user_dl = os.path.join(home, "Downloads")
	if os.path.exists(user_dl):
		DOWNLOADS_DIR = user_dl
	else:
		if _app_data_dir:
			try:
				os.makedirs(_app_data_dir, exist_ok=True)
			except Exception:
				pass
			DOWNLOADS_DIR = os.path.join(_app_data_dir, "downloads")
		else:
			DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")

# other defaults
DEFAULT_N_CONNS = int(os.environ.get("DEFAULT_N_CONNS", "4"))
DEFAULT_CONCURRENCY = int(os.environ.get("DEFAULT_CONCURRENCY", "2"))

# External Services
STEAMGRIDDB_API_KEY = os.environ.get("STEAMGRIDDB_API_KEY", "7bc101bec7908e8671f505a6612c4868")
