from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx

from app.core.config import Settings
from app.db.initialization import (
    create_engine_and_session_factory,
    initialize_test_database,
)
from app.db.seed.service import seed_database
from app.main import create_app


@asynccontextmanager
async def async_test_client(settings: Settings) -> AsyncIterator[httpx.AsyncClient]:
    engine, session_factory = create_engine_and_session_factory(settings)
    initialize_test_database(engine)
    seed_database(
        session_factory=session_factory,
        scenario_id=settings.default_scenario,
        seed=settings.default_seed,
    )
    engine.dispose()
    app = create_app(settings)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            yield client
