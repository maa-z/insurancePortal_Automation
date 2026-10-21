import uuid
import datetime
import asyncio
import json
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.run import AutomationRunModel
from ..models.audit import AuditEventModel
from ..models.review import HumanReviewModel
from ..schemas.run import (
    StartRunRequest,
    AutomationRunResponse,
    ReviewDecisionRequest,
    SubmissionApprovalRequest,
    HumanReviewResponse,
)
from ..schemas.audit import AuditEventResponse
from ..schemas.portal import PortalOutcome
from ..workflow.graph import PriorAuthWorkflowEngine
from ..review.manager import ReviewManager
from ..audit.logger import AuditLogger
from ..config import settings

router = APIRouter()

# Active in-memory workflow engines mapped by run_id
active_engines: Dict[str, PriorAuthWorkflowEngine] = {}


def _serialize_run(run: AutomationRunModel) -> AutomationRunResponse:
    outcome = None
    if run.outcome_data:
        outcome = PortalOutcome(**run.outcome_data)

    return AutomationRunResponse(
        run_id=run.run_id,
        patient_id=run.patient_id,
        state=run.state,
        current_page=run.current_page,
        created_at=run.created_at,
        updated_at=run.updated_at,
        is_paused=run.is_paused,
        fields_discovered_count=run.fields_discovered_count,
        fields_filled_count=run.fields_filled_count,
        pending_reviews_count=run.pending_reviews_count,
        conflicts_count=run.conflicts_count,
        ai_mode=run.ai_mode,
        model_name=run.model_name,
        outcome=outcome,
        error_message=run.error_message,
    )


@router.post("/automation/runs", response_model=AutomationRunResponse)
async def create_run(request: StartRunRequest, db: Session = Depends(get_db)):
    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"

    run = AutomationRunModel(
        run_id=run_id,
        patient_id=request.patient_id,
        state="CASE_CREATED",
        current_page="patient_info",
        ai_mode=request.ai_mode,
        model_name=(settings.GROQ_MODEL if settings.GROQ_API_KEY else settings.OPENAI_MODEL) if request.ai_mode == "llm" else "deterministic-mock",
        created_at=datetime.datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Initialize workflow engine
    engine = PriorAuthWorkflowEngine(
        run_id=run_id,
        patient_id=request.patient_id,
        ai_mode=request.ai_mode,
    )
    active_engines[run_id] = engine

    # Launch workflow asynchronously in the background
    asyncio.create_task(engine.run())

    return _serialize_run(run)


@router.get("/automation/runs/{run_id}", response_model=AutomationRunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(AutomationRunModel).filter_by(run_id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")
    return _serialize_run(run)


@router.post("/automation/runs/{run_id}/pause", response_model=AutomationRunResponse)
async def pause_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(AutomationRunModel).filter_by(run_id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")

    run.is_paused = True
    db.commit()

    engine = active_engines.get(run_id)
    if engine:
        engine.state_data.is_paused = True

    await AuditLogger.log_event(
        run_id=run_id,
        patient_id=run.patient_id,
        transition="PAUSED_BY_USER",
        portal_page=run.current_page,
        db=db,
    )

    return _serialize_run(run)


@router.post("/automation/runs/{run_id}/resume", response_model=AutomationRunResponse)
async def resume_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(AutomationRunModel).filter_by(run_id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")

    run.is_paused = False
    db.commit()

    engine = active_engines.get(run_id)
    if engine:
        engine.state_data.is_paused = False
        asyncio.create_task(engine.run())

    await AuditLogger.log_event(
        run_id=run_id,
        patient_id=run.patient_id,
        transition="RESUMED_BY_USER",
        portal_page=run.current_page,
        db=db,
    )

    return _serialize_run(run)


@router.post("/automation/runs/{run_id}/cancel", response_model=AutomationRunResponse)
async def cancel_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(AutomationRunModel).filter_by(run_id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")

    run.state = "CANCELLED"
    run.is_paused = False
    db.commit()

    engine = active_engines.get(run_id)
    if engine:
        await engine.cancel()

    await AuditLogger.log_event(
        run_id=run_id,
        patient_id=run.patient_id,
        transition="CANCELLED_BY_USER",
        portal_page=run.current_page,
        db=db,
    )

    return _serialize_run(run)


@router.get("/automation/runs/{run_id}/reviews", response_model=List[HumanReviewResponse])
def get_pending_reviews(run_id: str, db: Session = Depends(get_db)):
    reviews = (
        db.query(HumanReviewModel)
        .filter_by(run_id=run_id, status="PENDING")
        .order_by(HumanReviewModel.created_at.desc())
        .all()
    )
    return reviews


@router.post("/automation/runs/{run_id}/reviews/{review_id}/decision", response_model=AutomationRunResponse)
async def submit_review_decision(
    run_id: str,
    review_id: str,
    request: ReviewDecisionRequest,
    db: Session = Depends(get_db),
):
    review = await ReviewManager.resolve_review(
        db=db,
        review_id=review_id,
        decision=request.decision,
        edited_value=request.edited_value,
        reviewer_note=request.reviewer_note,
    )

    # Resume the engine with approved or edited value
    engine = active_engines.get(run_id)
    approved_val = request.edited_value if request.decision == "EDITED" else review.proposed_value
    if engine and request.decision in ("APPROVED", "EDITED"):
        asyncio.create_task(engine.resume_after_review(review.field_id, approved_val))

    run = db.query(AutomationRunModel).filter_by(run_id=run_id).first()
    return _serialize_run(run)


@router.post("/automation/runs/{run_id}/submission-approval", response_model=AutomationRunResponse)
async def submit_final_approval(
    run_id: str,
    request: SubmissionApprovalRequest,
    db: Session = Depends(get_db),
):
    engine = active_engines.get(run_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Active workflow engine not found.")

    asyncio.create_task(engine.execute_final_submission(request.approved, request.notes))

    run = db.query(AutomationRunModel).filter_by(run_id=run_id).first()
    return _serialize_run(run)


@router.get("/automation/runs/{run_id}/audit", response_model=List[AuditEventResponse])
def get_audit_timeline(run_id: str, db: Session = Depends(get_db)):
    events = (
        db.query(AuditEventModel)
        .filter_by(run_id=run_id)
        .order_by(AuditEventModel.timestamp.desc())
        .all()
    )
    return events


@router.get("/automation/runs/{run_id}/events")
async def stream_run_events(run_id: str):
    """Server-Sent Events (SSE) live event streaming."""
    queue = AuditLogger.subscribe(run_id)

    async def event_generator():
        try:
            # Yield initial connection heartbeat
            yield f"data: {json.dumps({'type': 'CONNECTED', 'run_id': run_id})}\n\n"
            while True:
                message = await queue.get()
                yield f"data: {json.dumps(message)}\n\n"
        except asyncio.CancelledError:
            AuditLogger.unsubscribe(run_id, queue)
        finally:
            AuditLogger.unsubscribe(run_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
