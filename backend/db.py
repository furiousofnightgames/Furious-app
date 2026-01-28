from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import event
from typing import Optional
from datetime import datetime
import os
import shutil
import time
from pathlib import Path

# --- ESTADO GLOBAL DO BANCO ---
_engine = None
_database_url = None
_db_file_path = None

def _sqlite_url_from_path(p: str) -> str:
    abs_path = Path(p).expanduser()
    try:
        abs_path = abs_path.resolve(strict=False)
    except Exception:
        abs_path = Path(os.path.abspath(str(abs_path)))
    posix_path = abs_path.as_posix()
    return f"sqlite:///{posix_path}"

def get_db_path() -> Path:
    """Calcula o caminho do banco baseado no ambiente."""
    global _db_file_path
    if _db_file_path:
        return _db_file_path

    env_db_path = os.environ.get("DB_PATH")
    env_app_data_dir = os.environ.get("APP_DATA_DIR")

    if env_db_path:
        _db_file_path = Path(env_db_path)
    elif env_app_data_dir:
        os.makedirs(env_app_data_dir, exist_ok=True)
        _db_file_path = Path(os.path.join(env_app_data_dir, 'data.db'))
    else:
        # Fallback padrão
        roaming = os.environ.get("APPDATA")
        if roaming:
            dest = os.path.join(roaming, "furiousapp")
            os.makedirs(dest, exist_ok=True)
            _db_file_path = Path(os.path.join(dest, "data.db"))
        else:
            _db_file_path = Path("./data.db")
    
    return _db_file_path

def get_engine():
    """Retorna o engine único, inicializando-o se necessário."""
    global _engine, _database_url
    if _engine is not None:
        return _engine

    db_path = get_db_path()
    _database_url = _sqlite_url_from_path(str(db_path))
    
    print(f"[DB-INIT] Inicializando motor SQL: {_database_url}")
    print(f"[DB-INIT] Arquivo existe? {db_path.exists()} (Tamanho: {db_path.stat().st_size if db_path.exists() else 0} bytes)")

    _engine = create_engine(
        _database_url,
        connect_args={"check_same_thread": False},
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600
    )

    # Configurar pragmas (Modo síncrono e direto)
    @event.listens_for(_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        # journal_mode=DELETE para garantir atualização imediata do arquivo principal (evita WAL ghosts)
        cursor.execute("PRAGMA journal_mode=DELETE")
        cursor.execute("PRAGMA synchronous=EXTRA")
        cursor.close()

    return _engine

def init_db():
    """Inicializa o banco e as tabelas."""
    from backend.models import models  # noqa: F401
    
    # Backup antes de mexer
    backup_database_file()
    
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    
    # Migrações manuais
    with engine.connect() as conn:
        _check_and_migrate_schema(conn)
    
    print(f"[DB-INIT] Banco pronto e migrado.")

def get_session() -> Session:
    """Retorna uma nova sessão SQLAlchemy."""
    return Session(get_engine())

def get_db_file_path() -> Path:
    """Retorna o caminho físico do banco (para auditoria)"""
    return get_db_path()

def backup_database_file():
    """Cria um backup se o banco existir e for antigo."""
    db_path = get_db_path()
    if not db_path or not db_path.exists():
        return
    
    try:
        backup_path = db_path.with_suffix('.db.bak')
        if db_path.stat().st_size > 0:
            if backup_path.exists():
                if (time.time() - backup_path.stat().st_mtime) < (6 * 3600):
                    return
            
            shutil.copy2(db_path, backup_path)
            print(f"[DB-BACKUP] Criado com sucesso: {backup_path}")
    except Exception as e:
        print(f"[DB-BACKUP] Falha: {e}")

def _check_and_migrate_schema(conn):
    """Verifica e aplica migrações manuais de schema."""
    def has_column(table: str, column: str) -> bool:
        r = conn.exec_driver_sql(f"PRAGMA table_info('{table}')")
        cols = [row[1] for row in r.fetchall()]
        return column in cols

    # ResolverAlias table
    conn.exec_driver_sql(
        "CREATE TABLE IF NOT EXISTS resolveralias ("
        "id INTEGER PRIMARY KEY, "
        "key TEXT NOT NULL UNIQUE, "
        "app_id INTEGER NOT NULL, "
        "created_at DATETIME, "
        "updated_at DATETIME"
        ")"
    )

    # GameMetadata table
    conn.exec_driver_sql(
        "CREATE TABLE IF NOT EXISTS gamemetadata ("
        "app_id INTEGER PRIMARY KEY, "
        "name TEXT, "
        "genres_json TEXT, "
        "developers_json TEXT, "
        "header_image_url TEXT, "
        "capsule_image_url TEXT, "
        "not_found_on_store INTEGER DEFAULT 0, "
        "updated_at DATETIME"
        ")"
    )
    
    # Check for missing columns
    if not has_column('gamemetadata', 'header_image_url'):
        conn.exec_driver_sql("ALTER TABLE gamemetadata ADD COLUMN header_image_url TEXT")
    if not has_column('gamemetadata', 'capsule_image_url'):
        conn.exec_driver_sql("ALTER TABLE gamemetadata ADD COLUMN capsule_image_url TEXT")
    if not has_column('gamemetadata', 'not_found_on_store'):
        conn.exec_driver_sql("ALTER TABLE gamemetadata ADD COLUMN not_found_on_store INTEGER DEFAULT 0")
    if not has_column('gamemetadata', 'type'):
        conn.exec_driver_sql("ALTER TABLE gamemetadata ADD COLUMN type TEXT")

    # Job table columns cleanup/add
    cols_to_add = {
        'k': 'INTEGER DEFAULT 4',
        'n_conns': 'INTEGER DEFAULT 4',
        'resume_on_start': 'INTEGER DEFAULT 1',
        'limit_bandwidth': 'INTEGER',
        'verify_ssl': 'INTEGER DEFAULT 1',
        'last_error': 'TEXT',
        'status_reason': 'TEXT',
        'downloaded': 'INTEGER DEFAULT 0',
        'free_space_at_pause': 'INTEGER',
        'size': 'INTEGER',
        'setup_executed': 'INTEGER DEFAULT 0',
        'started_at': 'DATETIME',
        'completed_at': 'DATETIME'
    }
    for col, type_def in cols_to_add.items():
        if not has_column('job', col):
            conn.exec_driver_sql(f"ALTER TABLE job ADD COLUMN {col} {type_def}")

    # Source columns
    if not has_column('source', 'data'):
        conn.exec_driver_sql("ALTER TABLE source ADD COLUMN data TEXT")

    # Item columns
    for col, typ in {'image':'TEXT', 'icon':'TEXT', 'thumbnail':'TEXT', 'seeders':'INTEGER', 'leechers':'INTEGER'}.items():
        if not has_column('item', col):
            conn.exec_driver_sql(f"ALTER TABLE item ADD COLUMN {col} {typ}")

    # Favorite columns
    if not has_column('favorite', 'image'):
        conn.exec_driver_sql("ALTER TABLE favorite ADD COLUMN image TEXT")

    # JobPart columns
    for col, typ in {'downloaded':'INTEGER DEFAULT 0', 'size':'INTEGER', 'status':"TEXT DEFAULT 'pending'", 'updated_at':'DATETIME'}.items():
        if not has_column('jobpart', col):
            conn.exec_driver_sql(f"ALTER TABLE jobpart ADD COLUMN {col} {typ}")

    # SteamApp table
    conn.exec_driver_sql(
        "CREATE TABLE IF NOT EXISTS steamapp ("
        "appid INTEGER PRIMARY KEY, "
        "name TEXT, "
        "normalized_name TEXT"
        ")"
    )
    if not has_column('steamapp', 'normalized_name'):
        conn.exec_driver_sql("ALTER TABLE steamapp ADD COLUMN normalized_name TEXT")
    
    # Indexes for SteamApp
    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_steamapp_name ON steamapp (name)")
    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_steamapp_normalized ON steamapp (normalized_name)")
