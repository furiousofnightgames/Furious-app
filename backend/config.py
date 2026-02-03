import os

# Optional environment variable to point to aria2 binary
ARIA2C_PATH = os.environ.get("ARIA2C_PATH")

_app_data_dir = os.environ.get("APP_DATA_DIR")

import pathlib

# Default download dir: prefer the user's Downloads folder when available
_env_dl = os.environ.get("DOWNLOADS_DIR")
if _env_dl:
	DOWNLOADS_DIR = os.path.abspath(_env_dl)
else:
	# Robust detection using pathlib
	try:
		home = pathlib.Path.home()
		user_dl = home / "Downloads"
		if user_dl.exists():
			DOWNLOADS_DIR = str(user_dl.absolute())
		else:
			DOWNLOADS_DIR = str(home.absolute())
	except Exception:
		# Absolute fallback to generic profile if detection fails completely
		DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")


# other defaults
DEFAULT_N_CONNS = int(os.environ.get("DEFAULT_N_CONNS", "4"))
DEFAULT_CONCURRENCY = int(os.environ.get("DEFAULT_CONCURRENCY", "2"))

# External Services (Obtenha sua chave em https://www.steamgriddb.com/profile/api)
STEAMGRIDDB_API_KEY = os.environ.get("STEAMGRIDDB_API_KEY", "SUA_CHAVE_AQUI")
