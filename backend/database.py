"""Persistence contains identifiers and bounded reports, never uploaded bytes."""

from sqlalchemy import Boolean, Float, ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from backend.config import settings


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)


class Session(Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner: Mapped[str] = mapped_column(String(36), index=True)
    expires: Mapped[float] = mapped_column(Float, index=True)
    authenticated: Mapped[bool] = mapped_column(Boolean, default=False)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner: Mapped[str] = mapped_column(String(36), index=True)
    operation: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="queued", index=True)
    created: Mapped[float] = mapped_column(Float)
    expires: Mapped[float] = mapped_column(Float, index=True)
    filenames: Mapped[str] = mapped_column(Text)
    declared_mimes: Mapped[str] = mapped_column(Text)
    options: Mapped[str] = mapped_column(Text)
    report: Mapped[str] = mapped_column(Text, default="{}")
    output_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error: Mapped[str | None] = mapped_column(String(128), nullable=True)


if settings.database_url.startswith("sqlite"):
    settings.storage.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
engine = create_engine(settings.database_url, pool_pre_ping=True,
                       connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def initialize_database():
    Base.metadata.create_all(engine)