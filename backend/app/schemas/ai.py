from typing import List, Optional, Any
from pydantic import BaseModel, Field


class EvidenceCitation(BaseModel):
    record_id: str
    source_type: str
    event_date: Optional[str] = None
    supporting_text: str
    directness: str = "direct"  # direct, inferred, historical


class ProposedAnswerSchema(BaseModel):
    patient_id: str
    page_id: str
    field_id: str
    question_text: str
    normalized_concept: str
    answer_type: str  # text, single_select, multi_select, numeric, date, boolean
    proposed_value: Any
    allowed_value_match: bool = True
    evidence: List[EvidenceCitation] = []
    conflicts: List[str] = []
    missing_information: List[str] = []
    validation_requirements: List[str] = []
    risk_level: str = "green"  # green, yellow, orange, red
    decision: str = "PROPOSED"  # PROPOSED, INSUFFICIENT_EVIDENCE, CONFLICT_REQUIRES_REVIEW, IDENTITY_MISMATCH, UNSUPPORTED_QUESTION, INVALID_ALLOWED_VALUE
    reason: str
