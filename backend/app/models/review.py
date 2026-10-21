import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text
from ..database import Base


class HumanReviewModel(Base):
    __tablename__ = "human_reviews"

    review_id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), index=True, nullable=False)
    patient_id = Column(String(32), index=True, nullable=False)
    page_id = Column(String(64), nullable=False)
    field_id = Column(String(128), nullable=False)
    question_text = Column(Text, nullable=False)
    proposed_value = Column(JSON, nullable=True)
    input_type = Column(String(32), default="text")
    allowed_values = Column(JSON, nullable=True)
    evidence = Column(JSON, default=list)
    conflicts = Column(JSON, default=list)
    missing_information = Column(JSON, default=list)
    risk_level = Column(String(16), default="orange")
    reason_for_escalation = Column(Text, nullable=False)
    status = Column(String(32), default="PENDING", index=True)  # PENDING, APPROVED, EDITED, REJECTED, UNAVAILABLE
    human_decision = Column(String(32), nullable=True)
    human_edit_value = Column(JSON, nullable=True)
    reviewer_note = Column(Text, nullable=True)
    screenshot_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
