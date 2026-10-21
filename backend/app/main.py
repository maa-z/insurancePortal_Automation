import sys
import asyncio
import logging
from contextlib import asynccontextmanager

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .api import api_router
from .patient_data.loader import PatientDataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("insurance_portal_agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    logger.info("Pre-loading synthetic patient records...")
    loader = PatientDataLoader.get_instance()
    patients = loader.get_all_patients()
    logger.info(f"Loaded {len(patients)} synthetic patient profiles.")

    yield

    logger.info("Shutting down Insurance Portal AI Agent application.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Insurance Prior Authorization Portal Closed-Loop AI Agent Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        loop="backend.app.loop:proactor_loop_factory",
        reload=True
    )
