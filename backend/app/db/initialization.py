from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.models import Base


def create_engine_and_session_factory(
    settings: Settings,
) -> tuple[Engine, sessionmaker[Session]]:
    connect_args: dict[str, bool] = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(settings.database_url, connect_args=connect_args)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return engine, session_factory


def initialize_database(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)
