from __future__ import annotations

from collections.abc import Callable

import pytest

from app.core.config import Settings
from tests.utils import async_test_client


@pytest.mark.anyio
async def test_health_response_matches_contract(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.headers["X-Request-ID"]
        assert response.json() == {
            "status": "healthy",
            "service": "agentlens-api",
            "version": "0.1.0",
        }


@pytest.mark.anyio
async def test_cors_headers_are_configurable(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert (
            response.headers["access-control-allow-origin"] == "http://localhost:3000"
        )
