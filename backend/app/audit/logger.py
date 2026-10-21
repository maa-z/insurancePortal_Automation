import uuid
import datetime
import asyncio
from typing import Optional, List, Any, Dict
from sqlalchemy.orm import Session
from ..models.audit import AuditEventModel
from ..database import SessionLocal


class AuditLogger:
    _subscribers: Dict[str, List[asyncio.Queue]] = {}

    @classmethod
    def subscribe(cls, run_id: str) -> asyncio.Queue:
        if run_id not in cls._subscribers:
            cls._subscribers[run_id] = []
        queue = asyncio.Queue()
        cls._subscribers[run_id].append(queue)
        return queue

    @classmethod
    def unsubscribe(cls, run_id: str, queue: asyncio.Queue):
        if run_id in cls._subscribers and queue in cls._subscribers[run_id]:
            cls._subscribers[run_id].remove(queue)

    @classmethod
    async def log_event(
        cls,
        run_id: str,
        patient_id: str,
        transition: Optional[str] = None,
        portal_page: Optional[str] = None,
        field_id: Optional[str] = None,
        question_text: Optional[str] = None,
        page_version: Optional[str] = None,
        retrieved_evidence_ids: Optional[List[str]] = None,
        proposed_answer: Optional[Any] = None,
        model_provider: Optional[str] = None,
        validation_results: Optional[Any] = None,
        filled_value: Optional[Any] = None,
        human_decision: Optional[str] = None,
        human_edit: Optional[Any] = None,
        risk_level: Optional[str] = None,
        error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None,
    ) -> AuditEventModel:
        event_id = f"EV-{uuid.uuid4().hex[:10]}"
        now = datetime.datetime.utcnow()

        event = AuditEventModel(
            event_id=event_id,
            run_id=run_id,
            patient_id=patient_id,
            timestamp=now,
            transition=transition,
            portal_page=portal_page,
            field_id=field_id,
            question_text=question_text,
            page_version=page_version,
            retrieved_evidence_ids=retrieved_evidence_ids,
            proposed_answer=proposed_answer,
            model_provider=model_provider,
            validation_results=validation_results,
            filled_value=filled_value,
            human_decision=human_decision,
            human_edit=human_edit,
            risk_level=risk_level,
            error=error,
            details=details,
        )

        # Persist to database
        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True
        try:
            db.add(event)
            db.commit()
            db.refresh(event)
        finally:
            if own_db:
                db.close()

        # Broadcast to SSE queues
        event_dict = {
            "event_id": event.event_id,
            "run_id": event.run_id,
            "patient_id": event.patient_id,
            "timestamp": now.isoformat(),
            "transition": event.transition,
            "portal_page": event.portal_page,
            "field_id": event.field_id,
            "question_text": event.question_text,
            "page_version": event.page_version,
            "retrieved_evidence_ids": event.retrieved_evidence_ids,
            "proposed_answer": event.proposed_answer,
            "model_provider": event.model_provider,
            "validation_results": event.validation_results,
            "filled_value": event.filled_value,
            "human_decision": event.human_decision,
            "human_edit": event.human_edit,
            "risk_level": event.risk_level,
            "error": event.error,
            "details": event.details,
        }

        if run_id in cls._subscribers:
            for q in list(cls._subscribers[run_id]):
                await q.put({"type": "AUDIT_EVENT", "event": event_dict})

        return event

    @classmethod
    async def broadcast(cls, run_id: str, message: Dict[str, Any]):
        if run_id in cls._subscribers:
            for q in list(cls._subscribers[run_id]):
                await q.put(message)
