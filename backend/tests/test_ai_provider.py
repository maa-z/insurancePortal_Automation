import pytest
from app.ai.mock_provider import MockAIProvider
from app.schemas.portal import FieldSnapshot
from app.schemas.ai import ProposedAnswerSchema


@pytest.mark.asyncio
async def test_mock_provider_demographics_proposal(patient_service):
    provider = MockAIProvider()
    field = FieldSnapshot(
        field_id="full_name",
        page_id="patient_info",
        question_text="Full Name",
        input_type="text",
        required=True,
        visible=True,
        page_version="v-1",
    )
    res = await provider.propose_answer("P1001", field, patient_service)
    assert isinstance(res, ProposedAnswerSchema)
    assert res.proposed_value == "Eleanor Vance"
    assert res.decision == "PROPOSED"
    assert res.risk_level == "green"
    assert len(res.evidence) > 0


@pytest.mark.asyncio
async def test_mock_provider_lung_egfr_proposal(patient_service):
    provider = MockAIProvider()
    field = FieldSnapshot(
        field_id="egfr_status",
        page_id="biomarkers",
        question_text="EGFR Mutation Status",
        input_type="select",
        allowed_values=["Positive (Exon 19 deletion)", "Negative"],
        required=True,
        visible=True,
        page_version="v-1",
    )
    res = await provider.propose_answer("P1002", field, patient_service)
    assert res.proposed_value == "Positive (Exon 19 deletion)"
    assert res.decision == "PROPOSED"


@pytest.mark.asyncio
async def test_mock_provider_conflicting_her2(patient_service):
    provider = MockAIProvider()
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
    res = await provider.propose_answer("P1006", field, patient_service)
    assert res.decision == "CONFLICT_REQUIRES_REVIEW"
    assert res.risk_level == "red"
    assert len(res.conflicts) > 0


@pytest.mark.asyncio
async def test_mock_provider_missing_kras(patient_service):
    provider = MockAIProvider()
    field = FieldSnapshot(
        field_id="crc_kras_status",
        page_id="biomarkers",
        question_text="KRAS Status",
        input_type="select",
        allowed_values=["Wild Type / Negative", "Mutant / Positive"],
        required=True,
        visible=True,
        page_version="v-1",
    )
    res = await provider.propose_answer("P1005", field, patient_service)
    assert res.decision == "INSUFFICIENT_EVIDENCE"
    assert res.risk_level == "red"
    assert len(res.missing_information) > 0


@pytest.mark.asyncio
async def test_mock_provider_identity_mismatch(patient_service):
    provider = MockAIProvider()
    field = FieldSnapshot(
        field_id="date_of_birth",
        page_id="patient_info",
        question_text="Date of Birth",
        input_type="date",
        required=True,
        visible=True,
        page_version="v-1",
    )
    res = await provider.propose_answer("P1008", field, patient_service)
    assert res.decision == "IDENTITY_MISMATCH"
    assert res.risk_level == "red"
    assert len(res.conflicts) > 0


@pytest.mark.asyncio
async def test_groq_provider_fallback_without_key(patient_service):
    from app.ai.llm_provider import GroqAIProvider
    # Ensure without key it delegates gracefully to mock provider
    provider = GroqAIProvider(api_key="")
    field = FieldSnapshot(
        field_id="full_name",
        page_id="patient_info",
        question_text="Full Name",
        input_type="text",
        required=True,
        visible=True,
        page_version="v-1",
    )
    res = await provider.propose_answer("P1001", field, patient_service)
    assert isinstance(res, ProposedAnswerSchema)
    assert res.proposed_value == "Eleanor Vance"
    assert res.decision == "PROPOSED"

