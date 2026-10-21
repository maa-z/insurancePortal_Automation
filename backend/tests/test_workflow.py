import pytest
from app.workflow.state import WORKFLOW_STATES, WorkflowStateData
from app.workflow.graph import PriorAuthWorkflowEngine


def test_workflow_states_comprehensive():
    assert "CASE_CREATED" in WORKFLOW_STATES
    assert "IDENTITY_VALIDATION" in WORKFLOW_STATES
    assert "IDENTITY_REVIEW_REQUIRED" in WORKFLOW_STATES
    assert "HUMAN_REVIEW_REQUIRED" in WORKFLOW_STATES
    assert "SUBMISSION_APPROVAL_REQUIRED" in WORKFLOW_STATES
    assert "OUTCOME_CAPTURED" in WORKFLOW_STATES
    assert len(WORKFLOW_STATES) >= 20


@pytest.mark.asyncio
async def test_identity_gate_halts_mismatched_patient():
    engine = PriorAuthWorkflowEngine(run_id="TEST-P1008", patient_id="P1008")
    await engine.run()
    assert engine.state_data.state == "IDENTITY_REVIEW_REQUIRED"
    assert engine.state_data.is_paused is True
    assert "identity mismatch" in engine.state_data.error_message.lower()


@pytest.mark.asyncio
async def test_submission_requires_explicit_approval():
    engine = PriorAuthWorkflowEngine(run_id="TEST-APPROVAL", patient_id="P1001")
    # Calling execute_final_submission with approved=False cancels the submission
    await engine.execute_final_submission(approved=False, notes="User declined")
    assert engine.state_data.state == "CANCELLED"
    assert "rejected" in engine.state_data.error_message.lower()
