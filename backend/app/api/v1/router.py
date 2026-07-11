from fastapi import APIRouter

from app.api.v1.endpoints.agents import router as agents_router
from app.api.v1.endpoints.alerts import router as alerts_router
from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.data_quality import router as data_quality_router
from app.api.v1.endpoints.forecast import router as forecast_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.overview import router as overview_router

router = APIRouter()
router.include_router(health_router)
router.include_router(overview_router)
router.include_router(data_quality_router)
router.include_router(forecast_router)
router.include_router(alerts_router)
router.include_router(analysis_router)
router.include_router(agents_router)
