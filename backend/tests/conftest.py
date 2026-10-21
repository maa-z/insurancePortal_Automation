import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.database import Base, engine, SessionLocal
from app.patient_data.loader import PatientDataLoader
from app.patient_data.service import PatientService


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup if needed


@pytest.fixture(scope="session")
def patient_loader():
    return PatientDataLoader.get_instance()


@pytest.fixture(scope="session")
def patient_service(patient_loader):
    return PatientService(loader=patient_loader)
