from fastapi import APIRouter
from ..config import settings

router = APIRouter()


@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "ai_mode": settings.AI_MODE,
        "headless": settings.HEADLESS,
    }
