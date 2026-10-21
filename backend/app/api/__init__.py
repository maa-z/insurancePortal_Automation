from fastapi import APIRouter
from .health import router as health_router
from .patients import router as patients_router
from .automation import router as automation_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(patients_router, tags=["Patients"])
api_router.include_router(automation_router, tags=["Automation"])

__all__ = ["api_router"]
