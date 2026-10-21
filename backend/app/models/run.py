import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, Text
from ..database import Base


class AutomationRunModel(Base):
    __tablename__ = "automation_runs"

    run_id = Column(String(64), primary_key=True, index=True)
    patient_id = Column(String(32), index=True, nullable=False)
    state = Column(String(64), default="CASE_CREATED", nullable=False)
    current_page = Column(String(64), default="patient_info", nullable=False)
    is_paused = Column(Boolean, default=False)
    fields_discovered_count = Column(Integer, default=0)
    fields_filled_count = Column(Integer, default=0)
    pending_reviews_count = Column(Integer, default=0)
    conflicts_count = Column(Integer, default=0)
    ai_mode = Column(String(16), default="mock")
    model_name = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    outcome_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
