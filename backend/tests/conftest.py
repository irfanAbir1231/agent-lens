from __future__ import annotations

import os
from collections.abc import Callable, Generator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.initialization import (
    create_engine_and_session_factory,
    initialize_test_database,
)
from app.db.seed.service import seed_database
from app.schemas.enums import ScenarioId

os.environ.setdefault("DATABASE_URL", "sqlite://")


@pytest.fixture
def make_settings(tmp_path: Path) -> Callable[..., Settings]:
    def _make(
        *,
        scenario: ScenarioId = ScenarioId.NORMAL_DAY,
        seed: int = 2026,
        suffix: str = "default",
    ) -> Settings:
        database_path = tmp_path / f"{suffix}-{scenario.value}-{seed}.sqlite3"
        return Settings(
            database_url=f"sqlite:///{database_path}",
            cors_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            default_scenario=scenario,
            default_seed=seed,
            log_level="INFO",
        )

    return _make


@pytest.fixture
def seeded_session_factory(
    make_settings: Callable[..., Settings],
) -> Generator[sessionmaker[Session]]:
    settings = make_settings()
    engine, session_factory = create_engine_and_session_factory(settings)
    initialize_test_database(engine)
    seed_database(
        session_factory=session_factory,
        scenario_id=settings.default_scenario,
        seed=settings.default_seed,
    )
    try:
        yield session_factory
    finally:
        engine.dispose()


@pytest.fixture
def db_session(
    seeded_session_factory: sessionmaker[Session],
) -> Generator[Session]:
    with seeded_session_factory() as session:
        yield session
