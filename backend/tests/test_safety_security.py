import pytest
from app.validation.rules import DeterministicValidator
from app.schemas.ai import ProposedAnswerSchema, EvidenceCitation
from app.schemas.portal import FieldSnapshot
from app.config import settings
from app.api.health import get_health


def test_api_key_never_exposed_in_healthcheck():
    health = get_health()
    assert "OPENAI_API_KEY" not in health
    assert "api_key" not in health
    assert "key" not in health


def test_evidence_from_another_patient_strictly_rejected():
    field = FieldSnapshot(
        field_id="primary_diagnosis",
        page_id="diagnosis",
        question_text="Primary Diagnosis Description",
        input_type="text",
        required=True,
        visible=True,
        page_version="v-1",
    )
    # Contaminated proposal: patient P1002 evidence supplied for active case P1001
    bad_proposal = ProposedAnswerSchema(
        patient_id="P1002",
        page_id="diagnosis",
        field_id="primary_diagnosis",
        question_text="Primary Diagnosis Description",
        normalized_concept="PRIMARY_DIAGNOSIS",
        answer_type="text",
        proposed_value="Non-small cell lung carcinoma",
        evidence=[EvidenceCitation(record_id="DIAG-1002-01", source_type="emr", supporting_text="NSCLC", directness="direct")],
        reason="Malicious cross-patient injection"
    )

    result = DeterministicValidator.validate_answer("P1001", bad_proposal, field)
    assert result.is_valid is False
    assert result.can_autofill is False
    assert result.risk_level == "red"
    assert "Cross-patient evidence contamination prevented" in result.escalation_reason


def test_unsupported_decision_never_autofilled():
    field = FieldSnapshot(
        field_id="rare_mutation",
        page_id="biomarkers",
        question_text="Rare Mutation X",
        input_type="text",
        required=True,
        visible=True,
        page_version="v-1",
    )
    proposal = ProposedAnswerSchema(
        patient_id="P1001",
        page_id="biomarkers",
        field_id="rare_mutation",
        question_text="Rare Mutation X",
        normalized_concept="UNKNOWN",
        answer_type="text",
        proposed_value=None,
        evidence=[],
        risk_level="red",
        decision="UNSUPPORTED_QUESTION",
        reason="Ontology does not recognize test"
    )

    result = DeterministicValidator.validate_answer("P1001", proposal, field)
    assert result.can_autofill is False


def test_conflicting_evidence_requires_human_review():
    field = FieldSnapshot(
        field_id="her2_status",
        page_id="biomarkers",
        question_text="HER2 Expression Status",
        input_type="select",
        allowed_values=["Positive", "Negative", "Equivocal"],
        required=True,
        visible=True,
        page_version="v-1",
    )
    proposal = ProposedAnswerSchema(
        patient_id="P1006",
        page_id="biomarkers",
        field_id="her2_status",
        question_text="HER2 Expression Status",
        normalized_concept="HER2_STATUS",
        answer_type="single_select",
        proposed_value="Equivocal",
        evidence=[],
        conflicts=["Discordant IHC 1- vs FISH amplified"],
        risk_level="red",
        decision="CONFLICT_REQUIRES_REVIEW",
        reason="Conflicting records"
    )

    result = DeterministicValidator.validate_answer("P1006", proposal, field)
    assert result.can_autofill is False
    assert result.risk_level == "red"
