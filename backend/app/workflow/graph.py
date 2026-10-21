import asyncio
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from ..models.run import AutomationRunModel
from ..models.review import HumanReviewModel
from ..database import SessionLocal
from ..schemas.portal import FieldSnapshot, PageSnapshot, PortalOutcome
from ..schemas.ai import ProposedAnswerSchema
from ..patient_data.service import PatientService
from ..validation.rules import DeterministicValidator
from ..ai.base import BaseAIProvider
from ..ai.mock_provider import MockAIProvider
from ..ai.llm_provider import OpenAIAIProvider, GroqAIProvider
from ..automation.browser import PlaywrightBrowserManager
from ..automation.observer import PortalObserver
from ..automation.filler import PortalFieldFiller
from ..review.manager import ReviewManager
from ..audit.logger import AuditLogger
from ..config import settings
from .state import WorkflowStateData

logger = logging.getLogger(__name__)


class PriorAuthWorkflowEngine:
    """
    Closed-loop orchestration state machine implementing:
    Observe -> Understand -> Retrieve -> Propose -> Validate -> Fill -> Verify -> Re-observe
    """

    def __init__(
        self,
        run_id: str,
        patient_id: str,
        ai_mode: str = "mock",
        browser_manager: Optional[PlaywrightBrowserManager] = None,
        patient_service: Optional[PatientService] = None,
    ):
        self.run_id = run_id
        self.patient_id = patient_id
        self.ai_mode = ai_mode.lower()
        self.browser_manager = browser_manager or PlaywrightBrowserManager()
        self.patient_service = patient_service or PatientService()

        # Select AI Provider
        if self.ai_mode == "llm":
            if settings.GROQ_API_KEY:
                self.ai_provider: BaseAIProvider = GroqAIProvider()
            elif settings.OPENAI_API_KEY:
                self.ai_provider: BaseAIProvider = OpenAIAIProvider()
            else:
                self.ai_provider = GroqAIProvider()
        else:
            self.ai_provider = MockAIProvider()

        self.state_data = WorkflowStateData(
            run_id=run_id,
            patient_id=patient_id,
            ai_mode=ai_mode,
        )
        self._is_cancelled = False

    async def _transition(self, new_state: str, error: Optional[str] = None):
        """Transition state machine, persist run record and broadcast audit event."""
        logger.info(f"[Run {self.run_id}] Transition: {self.state_data.state} -> {new_state}")
        self.state_data.state = new_state
        if error is not None:
            self.state_data.error_message = error

        db = SessionLocal()
        try:
            run = db.query(AutomationRunModel).filter_by(run_id=self.run_id).first()
            if not run:
                run = AutomationRunModel(
                    run_id=self.run_id,
                    patient_id=self.patient_id,
                    state=new_state,
                    current_page=self.state_data.current_page,
                    ai_mode=self.ai_mode,
                )
                db.add(run)
                db.commit()
                db.refresh(run)
            else:
                run.state = new_state
                run.current_page = self.state_data.current_page
                run.is_paused = self.state_data.is_paused
                run.error_message = self.state_data.error_message
                run.fields_discovered_count = len(self.state_data.fields_discovered)
                run.fields_filled_count = len(self.state_data.approved_values)
                # Count pending reviews
                pending_count = (
                    db.query(HumanReviewModel)
                    .filter_by(run_id=self.run_id, status="PENDING")
                    .count()
                )
                run.pending_reviews_count = pending_count

                if self.state_data.outcome:
                    run.outcome_data = self.state_data.outcome.model_dump()

                db.commit()

            # Broadcast SSE state update
            await AuditLogger.broadcast(
                self.run_id,
                {
                    "type": "STATE_CHANGE",
                    "run": {
                        "run_id": self.run_id,
                        "patient_id": self.patient_id,
                        "state": new_state,
                        "current_page": self.state_data.current_page,
                        "is_paused": self.state_data.is_paused,
                        "fields_discovered_count": len(self.state_data.fields_discovered),
                        "fields_filled_count": len(self.state_data.approved_values),
                        "pending_reviews_count": run.pending_reviews_count if run else 0,
                        "conflicts_count": run.conflicts_count if run else 0,
                        "ai_mode": self.ai_mode,
                        "outcome": self.state_data.outcome.model_dump() if self.state_data.outcome else None,
                        "error_message": self.state_data.error_message,
                    },
                },
            )

            # Log audit trail event
            await AuditLogger.log_event(
                run_id=self.run_id,
                patient_id=self.patient_id,
                transition=new_state,
                portal_page=self.state_data.current_page,
                page_version=self.state_data.page_version,
                error=error,
                db=db,
            )
        finally:
            db.close()

    async def run(self):
        """Main execution loop of the LangGraph state machine."""
        try:
            # 1. IDENTITY_VALIDATION
            await self._transition("IDENTITY_VALIDATION")
            identity_info = self.patient_service.get_patient_identity(self.patient_id)

            if not identity_info.get("identity_verified", True):
                self.state_data.is_paused = True
                await self._transition(
                    "IDENTITY_REVIEW_REQUIRED",
                    error="Patient identity mismatch between registration records and clinical master index.",
                )
                logger.warning(f"Run {self.run_id} quarantined at IDENTITY_REVIEW_REQUIRED.")
                return

            # 2. PATIENT_DATA_LOADED
            await self._transition("PATIENT_DATA_LOADED")

            # 3. PORTAL_SESSION_STARTING & READY
            await self._transition("PORTAL_SESSION_STARTING")
            page = await self.browser_manager.navigate_to_portal()
            await self._transition("PORTAL_SESSION_READY")

            # Page-by-page automation loop (Steps 1 through 7)
            while not self._is_cancelled:
                # Observe current visible portal page
                await self._transition("PAGE_OBSERVING")
                page_snapshot = await PortalObserver.observe_current_page(page)
                self.state_data.current_page = page_snapshot.page_id
                self.state_data.current_step = page_snapshot.current_step
                self.state_data.page_version = page_snapshot.page_version
                self.state_data.fields_discovered = page_snapshot.visible_fields

                await self._transition("FIELDS_DISCOVERED")
                await AuditLogger.broadcast(
                    self.run_id,
                    {
                        "type": "FIELDS_DISCOVERED",
                        "fields": [f.model_dump() for f in page_snapshot.visible_fields],
                    },
                )

                # Check if we have arrived at Step 7 Review & Submission
                if page_snapshot.current_step == 7 or page_snapshot.page_id == "review_submission":
                    self.state_data.is_paused = True
                    await self._transition("SUBMISSION_APPROVAL_REQUIRED")
                    logger.info(f"Run {self.run_id} arrived at Step 7. Awaiting explicit human submission approval.")
                    return

                # Branch loop on current page: Fill safe fields, re-observe for newly visible branch fields
                page_branch_cycle = 0
                max_cycles = settings.MAX_BRANCH_CYCLES_PER_PAGE

                while page_branch_cycle < max_cycles:
                    page_branch_cycle += 1
                    # Filter fields that need processing
                    unfilled_fields = [
                        f for f in page_snapshot.visible_fields
                        if f.field_id not in self.state_data.approved_values
                    ]

                    if not unfilled_fields:
                        break

                    for field in unfilled_fields:
                        if self._is_cancelled:
                            return

                        # Evidence Retrieving & Answer Proposing
                        await self._transition("EVIDENCE_RETRIEVING")
                        await self._transition("ANSWER_PROPOSING")
                        proposal = await self.ai_provider.propose_answer(
                            self.patient_id, field, self.patient_service
                        )
                        self.state_data.proposed_answers[field.field_id] = proposal

                        await AuditLogger.broadcast(
                            self.run_id,
                            {
                                "type": "ANSWER_PROPOSED",
                                "proposal": proposal.model_dump(),
                            },
                        )

                        # Deterministic Validation Gate
                        await self._transition("ANSWER_VALIDATING")
                        patient_obj = self.patient_service.loader.get_patient(self.patient_id)
                        known_conflicts = [c.model_dump() for c in patient_obj.known_conflicts] if patient_obj else []

                        val_result = DeterministicValidator.validate_answer(
                            active_patient_id=self.patient_id,
                            proposal=proposal,
                            field_snapshot=field,
                            known_conflicts=known_conflicts,
                        )

                        # Check if human review is required (Orange or Red risk, or invalid)
                        if not val_result.can_autofill:
                            self.state_data.is_paused = True
                            db = SessionLocal()
                            try:
                                review = await ReviewManager.create_review_request(
                                    db=db,
                                    run_id=self.run_id,
                                    patient_id=self.patient_id,
                                    field=field,
                                    proposal=proposal,
                                    reason=val_result.escalation_reason or "Clinical human sign-off policy.",
                                    risk_level=val_result.risk_level,
                                )
                            finally:
                                db.close()

                            await self._transition("HUMAN_REVIEW_REQUIRED")
                            logger.info(f"Paused for human review on field '{field.field_id}'.")
                            return

                        # Safe to auto-fill (Green / Yellow)
                        approved_value = proposal.proposed_value

                        # Field Filling
                        await self._transition("FIELD_FILLING")
                        fill_success = await PortalFieldFiller.fill_field(page, field, approved_value)

                        # Field Verifying in DOM
                        await self._transition("FIELD_VERIFYING")
                        await PortalFieldFiller.verify_filled_value(page, field, approved_value)
                        self.state_data.approved_values[field.field_id] = approved_value

                        # Log fill action
                        await AuditLogger.log_event(
                            run_id=self.run_id,
                            patient_id=self.patient_id,
                            transition="FIELD_FILLED_AND_VERIFIED",
                            portal_page=self.state_data.current_page,
                            field_id=field.field_id,
                            question_text=field.question_text,
                            page_version=page_snapshot.page_version,
                            retrieved_evidence_ids=[e.record_id for e in proposal.evidence],
                            proposed_answer=proposal.proposed_value,
                            model_provider=self.ai_mode,
                            validation_results=val_result.model_dump(),
                            filled_value=approved_value,
                            risk_level=val_result.risk_level,
                        )

                    # Re-scan page for dynamic branching questions (Metastatic details, Recurrence, Toxicity, etc.)
                    await self._transition("PAGE_RESCANNING")
                    new_snapshot = await PortalObserver.observe_current_page(page)

                    # Compare fingerprints / new fields
                    new_unfilled = [
                        f for f in new_snapshot.visible_fields
                        if f.field_id not in self.state_data.approved_values
                    ]

                    page_snapshot = new_snapshot
                    self.state_data.fields_discovered = new_snapshot.visible_fields
                    self.state_data.page_version = new_snapshot.page_version

                    if not new_unfilled:
                        # All visible fields on current step have been filled and verified!
                        break

                # Advance to next page
                await self._transition("PAGE_COMPLETED")
                advanced = await PortalFieldFiller.advance_to_next_page(page)
                if not advanced:
                    # Arrived at the final page or cannot advance further
                    break

        except Exception as e:
            err_msg = f"{type(e).__name__}: {str(e)}" if str(e) else type(e).__name__
            logger.error(f"Workflow execution failure in Run {self.run_id}: {err_msg}", exc_info=True)
            await self._transition("FAILED", error=err_msg)
            try:
                await self.browser_manager.close()
            except Exception:
                pass

    async def resume_after_review(self, field_id: str, approved_val: Any):
        """Resume workflow after reviewer approves or edits a field."""
        self.state_data.approved_values[field_id] = approved_val
        self.state_data.is_paused = False

        page = await self.browser_manager.get_current_page()
        if not page:
            page = await self.browser_manager.navigate_to_portal()

        # Fill the approved value into DOM
        field_match = next((f for f in self.state_data.fields_discovered if f.field_id == field_id), None)
        if field_match:
            await self._transition("FIELD_FILLING")
            await PortalFieldFiller.fill_field(page, field_match, approved_val)
            await self._transition("FIELD_VERIFYING")
            await PortalFieldFiller.verify_filled_value(page, field_match, approved_val)

        # Resume loop
        await self.run()

    async def execute_final_submission(self, approved: bool, notes: Optional[str] = None):
        """Submit the prior authorization to the portal simulator upon human attestation."""
        if not approved:
            await self._transition("CANCELLED", error="Submission rejected by human reviewer.")
            return

        page = await self.browser_manager.get_current_page()
        if not page:
            page = await self.browser_manager.navigate_to_portal()

        await self._transition("SUBMITTING")
        outcome = await PortalFieldFiller.submit_portal(page)

        if outcome:
            self.state_data.outcome = outcome
            await self._transition("OUTCOME_CAPTURED")
            await AuditLogger.broadcast(
                self.run_id,
                {
                    "type": "OUTCOME_CAPTURED",
                    "outcome": outcome.model_dump(),
                },
            )
            # Log final audit event
            await AuditLogger.log_event(
                run_id=self.run_id,
                patient_id=self.patient_id,
                transition="PORTAL_OUTCOME_CAPTURED",
                portal_page="submission_outcome",
                details={
                    "outcome": outcome.outcome,
                    "confirmation_number": outcome.confirmation_number,
                    "summary": outcome.summary,
                    "reasons": outcome.outstanding_review_reasons,
                },
            )
        else:
            await self._transition("FAILED", error="Failed to capture simulated portal outcome.")

    async def cancel(self):
        """Cancel workflow run."""
        self._is_cancelled = True
        self.state_data.is_paused = False
        await self._transition("CANCELLED")
        await self.browser_manager.close()
