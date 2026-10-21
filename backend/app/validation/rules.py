import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from ..schemas.ai import ProposedAnswerSchema
from ..schemas.portal import FieldSnapshot
from .risk import classify_field_risk


class ValidationResult(BaseModel):
    is_valid: bool
    can_autofill: bool
    risk_level: str  # green, yellow, orange, red
    errors: List[str] = []
    warnings: List[str] = []
    escalation_reason: Optional[str] = None


class DeterministicValidator:
    REFERENCE_DATE = datetime.date(2026, 8, 1)

    @classmethod
    def validate_answer(
        cls,
        active_patient_id: str,
        proposal: ProposedAnswerSchema,
        field_snapshot: FieldSnapshot,
        known_conflicts: Optional[List[Dict[str, Any]]] = None
    ) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []
        escalation_reasons: List[str] = []

        # 1. Patient identity consistency
        if proposal.patient_id != active_patient_id:
            errors.append(f"Patient mismatch: Proposal belongs to {proposal.patient_id}, but active case is {active_patient_id}")
            return ValidationResult(
                is_valid=False,
                can_autofill=False,
                risk_level="red",
                errors=errors,
                escalation_reason="Cross-patient evidence contamination prevented."
            )

        # 2. Check identity mismatch for patient (e.g. P1008)
        is_identity_mismatch = False
        if known_conflicts:
            for c in known_conflicts:
                if c.get("type") == "IDENTITY_MISMATCH":
                    is_identity_mismatch = True
                    errors.append(f"Identity Gate Failed: {c.get('description')}")
                    escalation_reasons.append(c.get("description", "Identity mismatch"))

        # 3. Check known clinical conflicts for this field (e.g. P1006 HER2)
        has_field_conflict = bool(proposal.conflicts)
        if known_conflicts:
            for c in known_conflicts:
                conflict_field = c.get("field", "").lower().replace("-", "_")
                clean_field_id = field_snapshot.field_id.lower().replace("-", "_")
                if conflict_field in clean_field_id or clean_field_id in conflict_field:
                    if c.get("type") == "CONFLICTING_EVIDENCE":
                        has_field_conflict = True
                        errors.append(f"Conflicting Evidence: {c.get('description')}")
                        escalation_reasons.append(c.get("description"))

        # 4. Check missing information requirements (e.g. P1005 KRAS)
        has_missing_info = bool(proposal.missing_information)
        if known_conflicts:
            for c in known_conflicts:
                conflict_field = c.get("field", "").lower().replace("-", "_")
                clean_field_id = field_snapshot.field_id.lower().replace("-", "_")
                if conflict_field in clean_field_id or clean_field_id in conflict_field:
                    if c.get("type") == "MISSING_EVIDENCE":
                        has_missing_info = True
                        errors.append(f"Missing Evidence: {c.get('description')}")
                        escalation_reasons.append(c.get("description"))

        # 5. Check allowed values match
        val = proposal.proposed_value
        if field_snapshot.allowed_values and val is not None:
            # Check if value matches an allowed value
            allowed_normalized = [str(a).strip().lower() for a in field_snapshot.allowed_values]
            if isinstance(val, list):
                invalid_items = [item for item in val if str(item).strip().lower() not in allowed_normalized]
                if invalid_items:
                    errors.append(f"Values {invalid_items} not in allowed options: {field_snapshot.allowed_values}")
            else:
                str_val = str(val).strip().lower()
                if str_val not in allowed_normalized:
                    # Fuzzy match check (e.g. "Postmenopausal" matches "Postmenopausal")
                    match_found = any(str_val in a or a in str_val for a in allowed_normalized)
                    if not match_found:
                        errors.append(f"Proposed value '{val}' is not among allowed portal values: {field_snapshot.allowed_values}")

        # 6. Check lab recency (30 days threshold) (e.g. P1007)
        is_outdated_lab = False
        clean_field_id = field_snapshot.field_id.lower().replace("-", "_")
        if "creatinine" in clean_field_id or "lab_collection_date" in clean_field_id:
            for ev in proposal.evidence:
                if ev.event_date:
                    try:
                        ev_dt = datetime.date.fromisoformat(ev.event_date)
                        delta = (cls.REFERENCE_DATE - ev_dt).days
                        if delta > 30:
                            is_outdated_lab = True
                            errors.append(f"Laboratory result date ({ev.event_date}) is {delta} days old, exceeding the 30-day clinical recency threshold.")
                            escalation_reasons.append(f"Lab result exceeds 30-day recency window ({delta} days old).")
                    except Exception:
                        pass

        if known_conflicts:
            for c in known_conflicts:
                if c.get("type") == "OUTDATED_LAB" and "creatinine" in clean_field_id:
                    is_outdated_lab = True
                    errors.append(c.get("description", "Outdated lab"))
                    escalation_reasons.append(c.get("description", "Outdated lab"))

        # 7. Check evidence existence for non-empty proposed values
        if val is not None and str(val).strip() != "" and str(val).strip() != "[]":
            if not proposal.evidence and clean_field_id not in ("patient_id", "authorization_type"):
                warnings.append("No supporting evidence citations linked to this proposed answer.")

        # Classify Risk Level
        directness = proposal.evidence[0].directness if proposal.evidence else "direct"
        risk_level = classify_field_risk(
            field_id=field_snapshot.field_id,
            has_conflicts=has_field_conflict,
            has_missing_info=has_missing_info,
            is_identity_mismatch=is_identity_mismatch,
            is_outdated_lab=is_outdated_lab,
            directness=directness,
        )

        is_valid = len(errors) == 0
        # Can autofill only if valid AND green/yellow risk. Orange and Red require human approval!
        can_autofill = is_valid and (risk_level in ("green", "yellow"))

        if not can_autofill and not escalation_reasons:
            if risk_level == "orange":
                escalation_reasons.append(f"Clinical policy requires human sign-off for {field_snapshot.field_id}.")
            elif errors:
                escalation_reasons.extend(errors)

        return ValidationResult(
            is_valid=is_valid,
            can_autofill=can_autofill,
            risk_level=risk_level,
            errors=errors,
            warnings=warnings,
            escalation_reason="; ".join(escalation_reasons) if escalation_reasons else None,
        )
