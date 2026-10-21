import datetime
import pytest
from app.schemas.ai import ProposedAnswerSchema, EvidenceCitation
from app.schemas.portal import FieldSnapshot
from app.validation.rules import DeterministicValidator
from app.validation.risk import classify_field_risk


def test_classify_field_risk_administrative_is_green():
    assert classify_field_risk("full_name") == "green"
    assert classify_field_risk("date_of_birth") == "green"
    assert classify_field_risk("member_id") == "green"


def test_classify_field_risk_direct_clinical_is_yellow():
    assert classify_field_risk("primary_diagnosis") == "yellow"
    assert classify_field_risk("creatinine") == "yellow"
    assert classify_field_risk("er_status") == "yellow"


def test_classify_field_risk_complex_is_orange():
    assert classify_field_risk("disease_stage") == "orange"
    assert classify_field_risk("prior_systemic_therapy") == "orange"
    assert classify_field_risk("line_of_therapy") == "orange"


def test_classify_field_risk_conflict_is_red():
    assert classify_field_risk("her2_status", has_conflicts=True) == "red"
    assert classify_field_risk("creatinine", is_outdated_lab=True) == "red"
    assert classify_field_risk("date_of_birth", is_identity_mismatch=True) == "red"


def test_validation_allowed_values_match():
    field = FieldSnapshot(
        field_id="er_status",
        page_id="biomarkers",
        question_text="Estrogen Receptor (ER) Status",
        input_type="select",
        allowed_values=["Positive", "Negative"],
        required=True,
        visible=True,
        page_version="v-1",
    )
    proposal = ProposedAnswerSchema(
        patient_id="P1001",
        page_id="biomarkers",
        field_id="er_status",
        question_text="ER Status",
        normalized_concept="ER_STATUS",
        answer_type="single_select",
        proposed_value="Positive",
        evidence=[EvidenceCitation(record_id="BIO-1", source_type="pathology", supporting_text="ER Positive", directness="direct")],
        reason="Direct result"
    )

    result = DeterministicValidator.validate_answer("P1001", proposal, field)
    assert result.is_valid is True
    assert result.can_autofill is True
    assert result.risk_level == "yellow"


def test_validation_allowed_values_invalid_rejected():
    field = FieldSnapshot(
        field_id="er_status",
        page_id="biomarkers",
        question_text="ER Status",
        input_type="select",
        allowed_values=["Positive", "Negative"],
        required=True,
        visible=True,
        page_version="v-1",
    )
    proposal = ProposedAnswerSchema(
        patient_id="P1001",
        page_id="biomarkers",
        field_id="er_status",
        question_text="ER Status",
        normalized_concept="ER_STATUS",
        answer_type="single_select",
        proposed_value="INVALID_OPTION_NOT_ALLOWED",
        evidence=[],
        reason="Invalid test"
    )

    result = DeterministicValidator.validate_answer("P1001", proposal, field)
    assert result.is_valid is False
    assert result.can_autofill is False
    assert any("not among allowed" in e.lower() for e in result.errors)


def test_validation_outdated_lab_triggers_red():
    field = FieldSnapshot(
        field_id="creatinine",
        page_id="lab_clinical",
        question_text="Serum Creatinine",
        input_type="number",
        required=True,
        visible=True,
        page_version="v-1",
    )
    # Lab drawn 144 days before reference date 2026-08-01
    proposal = ProposedAnswerSchema(
        patient_id="P1007",
        page_id="lab_clinical",
        field_id="creatinine",
        question_text="Serum Creatinine",
        normalized_concept="CREATININE",
        answer_type="numeric",
        proposed_value="1.35",
        evidence=[EvidenceCitation(record_id="LAB-OUTDATED", source_type="lab", event_date="2026-03-10", supporting_text="Creatinine 1.35", directness="direct")],
        reason="Drawn 144 days ago"
    )

    result = DeterministicValidator.validate_answer("P1007", proposal, field)
    assert result.risk_level == "red"
    assert result.can_autofill is False
    assert any("30-day" in e for e in result.errors)


def test_cross_patient_proposal_rejected_immediately():
    field = FieldSnapshot(
        field_id="full_name",
        page_id="patient_info",
        question_text="Full Name",
        input_type="text",
        required=True,
        visible=True,
        page_version="v-1",
    )
    # Proposal belongs to P1002, but active case is P1001!
    proposal = ProposedAnswerSchema(
        patient_id="P1002",
        page_id="patient_info",
        field_id="full_name",
        question_text="Full Name",
        normalized_concept="FULL_NAME",
        answer_type="text",
        proposed_value="Marcus Chen",
        evidence=[],
        reason="Mismatched patient"
    )

    result = DeterministicValidator.validate_answer("P1001", proposal, field)
    assert result.is_valid is False
    assert result.can_autofill is False
    assert result.risk_level == "red"
    assert "Cross-patient evidence contamination prevented" in result.escalation_reason
