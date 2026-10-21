from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..schemas.portal import FieldSnapshot, PageSnapshot, PortalOutcome
from ..schemas.ai import ProposedAnswerSchema


WORKFLOW_STATES = [
    "CASE_CREATED",
    "IDENTITY_VALIDATION",
    "IDENTITY_REVIEW_REQUIRED",
    "PATIENT_DATA_LOADED",
    "PORTAL_SESSION_STARTING",
    "PORTAL_SESSION_READY",
    "PAGE_OBSERVING",
    "FIELDS_DISCOVERED",
    "EVIDENCE_RETRIEVING",
    "ANSWER_PROPOSING",
    "ANSWER_VALIDATING",
    "HUMAN_REVIEW_REQUIRED",
    "FIELD_FILLING",
    "FIELD_VERIFYING",
    "PAGE_RESCANNING",
    "PAGE_REVIEW_REQUIRED",
    "PAGE_COMPLETED",
    "SUBMISSION_APPROVAL_REQUIRED",
    "SUBMITTING",
    "OUTCOME_CAPTURED",
    "FAILED",
    "CANCELLED",
]


class WorkflowStateData(BaseModel):
    run_id: str
    patient_id: str
    state: str = "CASE_CREATED"
    current_page: str = "patient_info"
    current_step: int = 1
    page_version: str = "v-init"
    is_paused: bool = False
    ai_mode: str = "mock"
    fields_discovered: List[FieldSnapshot] = []
    proposed_answers: Dict[str, ProposedAnswerSchema] = {}
    approved_values: Dict[str, Any] = {}
    pending_review_ids: List[str] = []
    branch_cycle_count: int = 0
    outcome: Optional[PortalOutcome] = None
    error_message: Optional[str] = None
