from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.models import Base


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def create_engine_and_session_factory(
    settings: Settings,
) -> tuple[Engine, sessionmaker[Session]]:
    database_url = normalize_database_url(settings.database_url)
    connect_args: dict[str, bool] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=not database_url.startswith("sqlite"),
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return engine, session_factory


def initialize_test_database(engine: Engine) -> None:
    """Create tables only for isolated, disposable local test databases."""
    Base.metadata.create_all(bind=engine)
