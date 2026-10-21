import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from ..database import Base


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, index=True, nullable=False)
    run_id = Column(String(64), index=True, nullable=False)
    patient_id = Column(String(32), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    transition = Column(String(64), nullable=True)
    portal_page = Column(String(64), nullable=True)
    field_id = Column(String(128), nullable=True)
    question_text = Column(Text, nullable=True)
    page_version = Column(String(64), nullable=True)
    retrieved_evidence_ids = Column(JSON, nullable=True)
    proposed_answer = Column(JSON, nullable=True)
    model_provider = Column(String(64), nullable=True)
    validation_results = Column(JSON, nullable=True)
    filled_value = Column(JSON, nullable=True)
    human_decision = Column(String(32), nullable=True)
    human_edit = Column(JSON, nullable=True)
    risk_level = Column(String(16), nullable=True)
    error = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
