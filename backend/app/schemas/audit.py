import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    run_id: str
    patient_id: str
    timestamp: datetime.datetime
    transition: Optional[str] = None
    portal_page: Optional[str] = None
    field_id: Optional[str] = None
    question_text: Optional[str] = None
    page_version: Optional[str] = None
    retrieved_evidence_ids: Optional[List[str]] = None
    proposed_answer: Optional[Any] = None
    model_provider: Optional[str] = None
    validation_results: Optional[Any] = None
    filled_value: Optional[Any] = None
    human_decision: Optional[str] = None
    human_edit: Optional[Any] = None
    risk_level: Optional[str] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
