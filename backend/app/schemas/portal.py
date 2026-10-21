from typing import List, Optional, Any
from pydantic import BaseModel, Field


class FieldSnapshot(BaseModel):
    field_id: str
    page_id: str
    question_text: str
    help_text: Optional[str] = None
    input_type: str = "text"  # text, number, date, textarea, select, radio, checkbox, multi-select
    allowed_values: Optional[List[str]] = None
    required: bool = True
    visible: bool = True
    current_value: Optional[Any] = None
    depends_on: Optional[List[str]] = None
    risk_category: str = "clinical"
    page_version: str


class PageSnapshot(BaseModel):
    page_id: str
    current_step: int
    page_version: str
    visible_fields: List[FieldSnapshot] = []


class PortalOutcome(BaseModel):
    outcome: str  # VERIFIED, CANCELLED, IN_INSPECTION
    confirmation_number: str
    timestamp: str
    summary: str
    outstanding_review_reasons: List[str] = []
