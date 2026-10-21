import uuid
import datetime
from typing import Optional, List, Any, Dict
from sqlalchemy.orm import Session
from ..models.review import HumanReviewModel
from ..schemas.portal import FieldSnapshot
from ..schemas.ai import ProposedAnswerSchema
from ..audit.logger import AuditLogger


class ReviewManager:
    @classmethod
    async def create_review_request(
        cls,
        db: Session,
        run_id: str,
        patient_id: str,
        field: FieldSnapshot,
        proposal: ProposedAnswerSchema,
        reason: str,
        risk_level: str = "orange",
    ) -> HumanReviewModel:
        review_id = f"REV-{uuid.uuid4().hex[:8]}"

        # Check if already exists for this field and run
        existing = (
            db.query(HumanReviewModel)
            .filter_by(run_id=run_id, field_id=field.field_id, status="PENDING")
            .first()
        )
        if existing:
            return existing

        review = HumanReviewModel(
            review_id=review_id,
            run_id=run_id,
            patient_id=patient_id,
            page_id=field.page_id,
            field_id=field.field_id,
            question_text=field.question_text,
            proposed_value=proposal.proposed_value,
            input_type=field.input_type,
            allowed_values=field.allowed_values,
            evidence=[e.model_dump() for e in proposal.evidence],
            conflicts=proposal.conflicts,
            missing_information=proposal.missing_information,
            risk_level=risk_level,
            reason_for_escalation=reason,
            status="PENDING",
            created_at=datetime.datetime.utcnow(),
        )

        db.add(review)
        db.commit()
        db.refresh(review)

        # Broadcast SSE review notification
        await AuditLogger.broadcast(
            run_id,
            {
                "type": "REVIEW_REQUIRED",
                "review": {
                    "review_id": review.review_id,
                    "run_id": review.run_id,
                    "patient_id": review.patient_id,
                    "page_id": review.page_id,
                    "field_id": review.field_id,
                    "question_text": review.question_text,
                    "proposed_value": review.proposed_value,
                    "input_type": review.input_type,
                    "allowed_values": review.allowed_values,
                    "evidence": review.evidence,
                    "conflicts": review.conflicts,
                    "missing_information": review.missing_information,
                    "risk_level": review.risk_level,
                    "reason_for_escalation": review.reason_for_escalation,
                    "status": review.status,
                    "created_at": review.created_at.isoformat(),
                },
            },
        )

        return review

    @classmethod
    async def resolve_review(
        cls,
        db: Session,
        review_id: str,
        decision: str,  # APPROVED, EDITED, REJECTED, UNAVAILABLE
        edited_value: Optional[Any] = None,
        reviewer_note: Optional[str] = None,
    ) -> HumanReviewModel:
        review = db.query(HumanReviewModel).filter_by(review_id=review_id).first()
        if not review:
            raise KeyError(f"Review {review_id} not found.")

        review.status = decision
        review.human_decision = decision
        review.human_edit_value = edited_value
        review.reviewer_note = reviewer_note
        review.resolved_at = datetime.datetime.utcnow()

        db.commit()
        db.refresh(review)

        # Log audit trail of human decision
        await AuditLogger.log_event(
            run_id=review.run_id,
            patient_id=review.patient_id,
            transition="HUMAN_REVIEW_RESOLVED",
            portal_page=review.page_id,
            field_id=review.field_id,
            question_text=review.question_text,
            human_decision=decision,
            human_edit=edited_value,
            risk_level=review.risk_level,
            details={"reviewer_note": reviewer_note},
            db=db,
        )

        return review
