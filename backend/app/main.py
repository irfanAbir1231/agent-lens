from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api.router import router as api_router
from app.core.config import Settings, get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import bind_request_id, clear_request_id, setup_logging
from app.db.initialization import create_engine_and_session_factory

logger = logging.getLogger(__name__)


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp, header_name: str) -> None:
        self._app = app
        self._header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        request_id = _request_id_from_scope(scope) or str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        bind_request_id(request_id)
        started_at = perf_counter()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append(self._header_name, request_id)
            await send(message)

        try:
            await self._app(scope, receive, send_wrapper)
        finally:
            duration_ms = (perf_counter() - started_at) * 1000
            logger.info(
                "request_completed method=%s path=%s duration_ms=%.2f",
                scope.get("method", "-"),
                scope.get("path", "-"),
                duration_ms,
            )
            clear_request_id()


def _request_id_from_scope(scope: Scope) -> str | None:
    header_name = b"x-request-id"
    for key, value in scope.get("headers", []):
        if key == header_name:
            return value.decode("utf-8")
    return None


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or get_settings()
    setup_logging(active_settings.log_level)
    engine, session_factory = create_engine_and_session_factory(active_settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        engine.dispose()

    app = FastAPI(
        title=active_settings.app_name,
        version=active_settings.app_version,
        lifespan=lifespan,
    )
    app.state.settings = active_settings
    app.state.engine = engine
    app.state.session_factory = session_factory

    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RequestIdMiddleware,
        header_name=active_settings.request_id_header,
    )

    register_exception_handlers(app)

    app.include_router(api_router)
    return app


app = create_app()
