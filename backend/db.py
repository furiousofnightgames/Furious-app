from sqlmodel import SQLModel, Session, create_engine
from typing import Optional
from datetime import datetime
import os
from pathlib import Path

_env_db_path = os.environ.get("DB_PATH")
_env_app_data_dir = os.environ.get("APP_DATA_DIR")


def _sqlite_url_from_path(p: str) -> str:
    abs_path = Path(p).expanduser()
    try:
        abs_path = abs_path.resolve(strict=False)
    except Exception:
        abs_path = Path(os.path.abspath(str(abs_path)))
    posix_path = abs_path.as_posix()
    return f"sqlite:///{posix_path}"

if _env_db_path:
    DATABASE_URL = _sqlite_url_from_path(_env_db_path)
elif _env_app_data_dir:
    os.makedirs(_env_app_data_dir, exist_ok=True)
    DATABASE_URL = _sqlite_url_from_path(os.path.join(_env_app_data_dir, 'data.db'))
else:
    legacy_local_db = Path("./data.db")
    if legacy_local_db.exists():
        DATABASE_URL = "sqlite:///./data.db"
    else:
        _local_app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if _local_app_data:
            _default_dir = os.path.join(_local_app_data, "furious-app")
            os.makedirs(_default_dir, exist_ok=True)
            DATABASE_URL = _sqlite_url_from_path(os.path.join(_default_dir, 'data.db'))
        else:
            DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_size=20,           # Aumentado de 5 para 20
    max_overflow=30,        # Permite 30 conexões extras temporárias
    pool_pre_ping=True,     # Verifica conexões antes de usar
    pool_recycle=3600       # Recicla conexões após 1 hora
)


def init_db():
    from backend.models import models  # noqa: F401
    try:
        print(f"[DB] Using DATABASE_URL: {DATABASE_URL}")
    except Exception:
        pass
    SQLModel.metadata.create_all(engine)
    # Simple migration: add missing columns that might be added to models later
    with engine.connect() as conn:
        def has_column(table: str, column: str) -> bool:
            r = conn.exec_driver_sql(f"PRAGMA table_info('{table}')")
            cols = [row[1] for row in r.fetchall()]
            return column in cols

        # Job table columns
        if not has_column('job', 'k'):
            conn.exec_driver_sql("ALTER TABLE job ADD COLUMN k INTEGER DEFAULT 4")
        if not has_column('job', 'n_conns'):
            conn.exec_driver_sql("ALTER TABLE job ADD COLUMN n_conns INTEGER DEFAULT 4")
        if not has_column('job', 'resume_on_start'):
            conn.exec_driver_sql("ALTER TABLE job ADD COLUMN resume_on_start INTEGER DEFAULT 1")
        if not has_column('job', 'limit_bandwidth'):
            conn.exec_driver_sql("ALTER TABLE job ADD COLUMN limit_bandwidth INTEGER")
        if not has_column('job', 'verify_ssl'):
            conn.exec_driver_sql("ALTER TABLE job ADD COLUMN verify_ssl INTEGER DEFAULT 1")
        if not has_column('job', 'last_error'):
            conn.exec_driver_sql("ALTER TABLE job ADD COLUMN last_error TEXT")
        if not has_column('job', 'size'):
            conn.exec_driver_sql("ALTER TABLE job ADD COLUMN size INTEGER")

        # Source table columns
        if not has_column('source', 'data'):
            conn.exec_driver_sql("ALTER TABLE source ADD COLUMN data TEXT")

        # Item table columns (para imagens/avatares)
        if not has_column('item', 'image'):
            conn.exec_driver_sql("ALTER TABLE item ADD COLUMN image TEXT")
        if not has_column('item', 'icon'):
            conn.exec_driver_sql("ALTER TABLE item ADD COLUMN icon TEXT")
        if not has_column('item', 'thumbnail'):
            conn.exec_driver_sql("ALTER TABLE item ADD COLUMN thumbnail TEXT")

        # JobPart table columns
        if not has_column('jobpart', 'downloaded'):
            conn.exec_driver_sql("ALTER TABLE jobpart ADD COLUMN downloaded INTEGER DEFAULT 0")
        if not has_column('jobpart', 'size'):
            conn.exec_driver_sql("ALTER TABLE jobpart ADD COLUMN size INTEGER")
        if not has_column('jobpart', 'status'):
            conn.exec_driver_sql("ALTER TABLE jobpart ADD COLUMN status TEXT DEFAULT 'pending'")
        if not has_column('jobpart', 'updated_at'):
            conn.exec_driver_sql("ALTER TABLE jobpart ADD COLUMN updated_at DATETIME")


def get_session() -> Session:
    return Session(engine)
