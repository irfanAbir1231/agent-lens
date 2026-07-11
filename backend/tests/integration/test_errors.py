from __future__ import annotations

from collections.abc import Callable

import pytest

from app.core.config import Settings
from tests.utils import async_test_client


def assert_structured_error(
    body: dict[str, object],
    *,
    expected_code: str,
    request_id: str,
) -> None:
    assert set(body) == {"code", "message", "details", "request_id"}
    assert body["code"] == expected_code
    assert body["request_id"] == request_id


@pytest.mark.anyio
async def test_unknown_route_returns_structured_404(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.get("/api/v1/not-real")

        assert response.status_code == 404
        assert response.headers["X-Request-ID"]
        body = response.json()
        assert_structured_error(
            body,
            expected_code="route_not_found",
            request_id=response.headers["X-Request-ID"],
        )
        assert body["message"] == "The requested resource was not found."
        assert body["details"] == {"path": "/api/v1/not-real"}


@pytest.mark.anyio
async def test_validation_errors_use_structured_public_contract(
    make_settings: Callable[..., Settings],
) -> None:
    async with async_test_client(make_settings()) as client:
        response = await client.get(
            "/api/v1/agents", params={"page": 0, "page_size": 2}
        )

        assert response.status_code == 422
        assert response.headers["X-Request-ID"]
        body = response.json()
        assert_structured_error(
            body,
            expected_code="request_validation_error",
            request_id=response.headers["X-Request-ID"],
        )
        assert body["message"] == "The request could not be validated."
        assert body["details"] == [
            {
                "location": "query/page",
                "message": "Input should be greater than or equal to 1",
            }
        ]
