from __future__ import annotations

from fastapi import APIRouter, Request

from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(service=settings.app_name, version=settings.app_version)
