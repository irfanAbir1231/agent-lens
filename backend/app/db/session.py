from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.orm import Session


async def get_db_session(request: Request) -> AsyncGenerator[Session]:
    session_factory = request.app.state.session_factory
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
