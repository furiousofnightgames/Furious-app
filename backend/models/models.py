from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    title: Optional[str] = None
    data: Optional[str] = None  # Para armazenar JSON colado como string
    created_at: datetime = Field(default_factory=datetime.now)

    items: List["Item"] = Relationship(back_populates="source")


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: Optional[int] = Field(default=None, foreign_key="source.id")
    name: str
    url: str
    size: Optional[int] = None
    category: Optional[str] = None
    type: Optional[str] = None  # Subcategoria/tipo do item
    image: Optional[str] = None  # URL da imagem/thumbnail do item
    icon: Optional[str] = None  # URL de um ícone alternativo
    thumbnail: Optional[str] = None  # URL de uma miniatura
    created_at: datetime = Field(default_factory=datetime.now)
    seeders: Optional[int] = Field(default=None)
    leechers: Optional[int] = Field(default=None)

    source: Optional[Source] = Relationship(back_populates="items")


class Favorite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int
    item_id: int
    name: str
    url: str
    image: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: Optional[int] = Field(default=None, foreign_key="item.id")
    dest: Optional[str] = None
    # acceleration parameters
    k: int = 4  # number of parts
    n_conns: int = 4  # parallel connections per file total
    resume_on_start: bool = True
    limit_bandwidth: Optional[int] = None  # bytes/s limit (not yet implemented)
    verify_ssl: bool = True
    status: str = "queued"  # queued, running, paused, completed, failed
    progress: float = 0.0
    speed: Optional[float] = None  # bytes/s
    size: Optional[int] = None  # tamanho total do arquivo em bytes
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_error: Optional[str] = None
    status_reason: Optional[str] = None # Motivo de status especial (ex: falta de espaço)
    downloaded: int = 0 # Bytes baixados persistidos
    free_space_at_pause: Optional[int] = None # Espaço livre capturado no momento do erro/pausa
    setup_executed: bool = Field(default=False) # Indica se o instalador foi executado pelo usuário
    started_at: Optional[datetime] = None # Momento em que o download realmente saiu da fila
    completed_at: Optional[datetime] = None # Momento da conclusão com sucesso


class JobPart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: Optional[int] = Field(default=None, foreign_key="job.id")
    index: int
    start: Optional[int] = None
    end: Optional[int] = None
    downloaded: int = 0
    path: Optional[str] = None
    # track progress within part
    size: Optional[int] = None
    status: str = "pending"  # pending, running, completed, failed
    updated_at: datetime = Field(default_factory=datetime.now)


class ResolverAlias(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Key derived from the base title / session cache key (stable, sanitized)
    key: str = Field(index=True, unique=True)
    app_id: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class GameMetadata(SQLModel, table=True):
    """Caches detailed Steam metadata for fast library-wide filtering"""
    app_id: int = Field(primary_key=True)
    name: Optional[str] = None
    genres_json: Optional[str] = None # Stringified list of genres
    developers_json: Optional[str] = None # Stringified list of developers
    header_image_url: Optional[str] = None # Cached header image
    capsule_image_url: Optional[str] = None # Cached capsule image
    type: Optional[str] = None # game, dlc, hardware, music
    not_found_on_store: bool = Field(default=False) # Flag for non-Steam/Indie games
    updated_at: datetime = Field(default_factory=datetime.now)
