import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from .portal import PortalOutcome


class StartRunRequest(BaseModel):
    patient_id: str
    ai_mode: str = "mock"


class AutomationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: str
    patient_id: str
    state: str
    current_page: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_paused: bool
    fields_discovered_count: int
    fields_filled_count: int
    pending_reviews_count: int
    conflicts_count: int
    ai_mode: str
    model_name: Optional[str] = None
    outcome: Optional[PortalOutcome] = None
    error_message: Optional[str] = None


class ReviewDecisionRequest(BaseModel):
    decision: str  # APPROVED, EDITED, REJECTED, UNAVAILABLE
    edited_value: Optional[Any] = None
    reviewer_note: Optional[str] = None


class SubmissionApprovalRequest(BaseModel):
    approved: bool
    notes: Optional[str] = None


class HumanReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: str
    run_id: str
    patient_id: str
    page_id: str
    field_id: str
    question_text: str
    proposed_value: Any
    input_type: str
    allowed_values: Optional[List[str]] = None
    evidence: List[Dict[str, Any]] = []
    conflicts: List[str] = []
    missing_information: List[str] = []
    risk_level: str
    reason_for_escalation: str
    status: str
    human_decision: Optional[str] = None
    human_edit_value: Optional[Any] = None
    reviewer_note: Optional[str] = None
    screenshot_url: Optional[str] = None
    created_at: datetime.datetime
    resolved_at: Optional[datetime.datetime] = None
