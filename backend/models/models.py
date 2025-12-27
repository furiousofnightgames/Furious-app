from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    title: Optional[str] = None
    data: Optional[str] = None  # Para armazenar JSON colado como string
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    created_at: datetime = Field(default_factory=datetime.utcnow)

    source: Optional[Source] = Relationship(back_populates="items")


class Favorite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int
    item_id: int
    name: str
    url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_error: Optional[str] = None


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
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ResolverAlias(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Key derived from the base title / session cache key (stable, sanitized)
    key: str = Field(index=True, unique=True)
    app_id: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
