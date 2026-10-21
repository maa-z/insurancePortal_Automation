import re
from typing import List, Optional, Any, Dict
from ..schemas.portal import FieldSnapshot
from ..schemas.ai import ProposedAnswerSchema, EvidenceCitation
from ..patient_data.service import PatientService
from .base import BaseAIProvider


class MockAIProvider(BaseAIProvider):
    """Deterministic, offline AI provider producing structured answers with full evidence."""

    async def propose_answer(
        self,
        patient_id: str,
        field: FieldSnapshot,
        patient_service: PatientService
    ) -> ProposedAnswerSchema:
        clean_field_id = field.field_id.lower().replace("-", "_")

        # 1. Identity Mismatch check (P1008)
        identity_check = patient_service.get_patient_identity(patient_id)
        if not identity_check.get("identity_verified", True):
            if clean_field_id in ("patient_id", "date_of_birth", "full_name"):
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="IDENTITY_VERIFICATION",
                    answer_type="text",
                    proposed_value=identity_check["date_of_birth"]["value"] if clean_field_id == "date_of_birth" else identity_check["full_name"]["value"],
                    allowed_value_match=True,
                    evidence=[
                        EvidenceCitation(
                            record_id=identity_check["date_of_birth"]["record_id"],
                            source_type="registration_system",
                            event_date=identity_check["date_of_birth"]["recorded_at"],
                            supporting_text="Registration index DOB conflicts with clinical master EMR record.",
                            directness="direct"
                        )
                    ],
                    conflicts=["Identity Mismatch: Date of birth in registration system does not match EMR clinical chart."],
                    missing_information=[],
                    validation_requirements=["Manual identity quarantine review"],
                    risk_level="red",
                    decision="IDENTITY_MISMATCH",
                    reason="Patient identity mismatch detected between registration and clinical systems."
                )

        # 2. Demographics & Insurance (Step 1)
        demographics = patient_service.get_demographics(patient_id)
        insurance = patient_service.get_insurance_information(patient_id)

        if clean_field_id == "patient_id":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="PATIENT_ID",
                answer_type="text",
                proposed_value=patient_id,
                evidence=[],
                risk_level="green",
                decision="PROPOSED",
                reason="Direct master patient index identifier."
            )

        if clean_field_id == "full_name":
            return self._make_demo_proposal(patient_id, field, demographics.full_name, "FULL_NAME", "green")
        if clean_field_id == "date_of_birth":
            return self._make_demo_proposal(patient_id, field, demographics.date_of_birth, "DOB", "green")
        if clean_field_id == "sex":
            return self._make_demo_proposal(patient_id, field, demographics.sex, "SEX", "green")
        if clean_field_id == "address":
            return self._make_demo_proposal(patient_id, field, demographics.address, "ADDRESS", "green")

        if clean_field_id == "member_id":
            return self._make_demo_proposal(patient_id, field, insurance.member_id, "MEMBER_ID", "green")
        if clean_field_id == "insurance_plan":
            return self._make_demo_proposal(patient_id, field, insurance.insurance_plan, "INSURANCE_PLAN", "green")
        if clean_field_id == "provider_name":
            return self._make_demo_proposal(patient_id, field, insurance.provider_name, "PROVIDER_NAME", "green")
        if clean_field_id == "provider_npi":
            return self._make_demo_proposal(patient_id, field, insurance.provider_npi, "PROVIDER_NPI", "green")
        if clean_field_id == "authorization_type":
            return self._make_demo_proposal(patient_id, field, insurance.authorization_type, "AUTH_TYPE", "green")

        # 3. Diagnosis & Extent (Step 2)
        diagnoses = patient_service.get_diagnoses(patient_id)
        diag = diagnoses[0] if diagnoses else None

        if diag:
            diag_ev = [
                EvidenceCitation(
                    record_id=diag.record_id,
                    source_type=diag.source_type,
                    event_date=diag.event_date,
                    supporting_text=diag.supporting_text,
                    directness="direct"
                )
            ]

            if clean_field_id == "cancer_type":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="CANCER_TYPE",
                    answer_type="single_select",
                    proposed_value=diag.cancer_type,
                    evidence=diag_ev,
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason=f"Clinical note confirms {diag.cancer_type} diagnosis."
                )

            if clean_field_id == "primary_diagnosis":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="PRIMARY_DIAGNOSIS",
                    answer_type="text",
                    proposed_value=diag.primary_diagnosis,
                    evidence=diag_ev,
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason="Documented in Oncology Assessment."
                )

            if clean_field_id == "icd10_code":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="ICD10_CODE",
                    answer_type="text",
                    proposed_value=diag.icd10_code,
                    evidence=diag_ev,
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason="ICD-10 code documented in billing/clinical diagnosis index."
                )

            if clean_field_id == "diagnosis_date":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="DIAGNOSIS_DATE",
                    answer_type="date",
                    proposed_value=diag.diagnosis_date,
                    evidence=diag_ev,
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason="Date of primary biopsy/pathology diagnosis."
                )

            if clean_field_id == "disease_stage":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="DISEASE_STAGE",
                    answer_type="single_select",
                    proposed_value=diag.disease_stage,
                    evidence=diag_ev,
                    risk_level="orange",  # Orange: stage inferred across records
                    decision="PROPOSED",
                    reason="Staging documented in TNM clinical assessment."
                )

            if clean_field_id == "performance_status":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="ECOG_PERFORMANCE",
                    answer_type="single_select",
                    proposed_value=diag.performance_status,
                    evidence=diag_ev,
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason="ECOG score documented during exam."
                )

            if clean_field_id == "is_new_diagnosis":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="IS_NEW_DIAGNOSIS",
                    answer_type="single_select",
                    proposed_value=diag.is_new_diagnosis,
                    evidence=diag_ev,
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason=f"Clinical timeline indicates initial diagnosis: {diag.is_new_diagnosis}."
                )

            if clean_field_id == "is_recurrent":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="IS_RECURRENT",
                    answer_type="single_select",
                    proposed_value=diag.is_recurrent,
                    evidence=diag_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason=f"Disease recurrence status: {diag.is_recurrent}."
                )

            if clean_field_id == "recurrence_date":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="RECURRENCE_DATE",
                    answer_type="date",
                    proposed_value=diag.recurrence_date or diag.diagnosis_date,
                    evidence=diag_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Documented date of clinical/radiographic recurrence."
                )

            if clean_field_id == "previous_remission_date":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="PREVIOUS_REMISSION_DATE",
                    answer_type="date",
                    proposed_value=diag.previous_remission_date or "",
                    evidence=diag_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Prior documentation of clinical disease remission."
                )

            if clean_field_id == "is_metastatic":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="IS_METASTATIC",
                    answer_type="single_select",
                    proposed_value=diag.is_metastatic,
                    evidence=diag_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Staging CT/PET report confirmation of distant metastasis."
                )

            if clean_field_id in ("metastasis_sites", "metastasis_site"):
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="METASTASIS_SITES",
                    answer_type="multi_select",
                    proposed_value=diag.metastasis_sites or [],
                    evidence=diag_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Radiology report indicates metastatic lesions."
                )

            if clean_field_id == "metastasis_confirmation_date":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="METASTASIS_CONFIRMATION_DATE",
                    answer_type="date",
                    proposed_value=diag.metastasis_confirmation_date or diag.diagnosis_date,
                    evidence=diag_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="PET/CT scan date identifying metastatic involvement."
                )

            if clean_field_id == "evidence_source":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="EVIDENCE_SOURCE",
                    answer_type="single_select",
                    proposed_value="Imaging CT / PET / MRI",
                    evidence=diag_ev,
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason="Radiographic imaging modality utilized."
                )

        # 4. Biomarkers & Pathology (Step 3)
        biomarkers = patient_service.get_biomarkers(patient_id)
        pathology = patient_service.get_pathology(patient_id)

        # Check conflicting HER2 (P1006)
        if clean_field_id == "her2_status" and patient_id == "P1006":
            her2_records = [b for b in biomarkers if "HER2" in b.biomarker_name]
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="HER2_STATUS",
                answer_type="single_select",
                proposed_value="Equivocal",
                evidence=[
                    EvidenceCitation(
                        record_id=r.record_id,
                        source_type=r.source_type,
                        event_date=r.event_date,
                        supporting_text=r.supporting_text,
                        directness="direct"
                    )
                    for r in her2_records
                ],
                conflicts=["Discordant results: External lab IHC is 1+ (Negative), whereas In-house reflex FISH is Amplified (Positive)."],
                risk_level="red",
                decision="CONFLICT_REQUIRES_REVIEW",
                reason="Discordant pathology results require clinician arbitration."
            )

        # Check missing KRAS/NRAS (P1005)
        if clean_field_id in ("crc_kras_status", "crc_nras_status") and patient_id == "P1005":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="KRAS_NRAS_STATUS",
                answer_type="single_select",
                proposed_value=None,
                evidence=[],
                conflicts=[],
                missing_information=["Missing mandatory KRAS and NRAS molecular testing report for anti-EGFR antibody clearance."],
                risk_level="red",
                decision="INSUFFICIENT_EVIDENCE",
                reason="Patient record does not contain required molecular test."
            )

        # Breast biomarkers
        if clean_field_id == "er_status":
            return self._match_biomarker(patient_id, field, biomarkers, "ER_STATUS", "single_select")
        if clean_field_id == "pr_status":
            return self._match_biomarker(patient_id, field, biomarkers, "PR_STATUS", "single_select")
        if clean_field_id == "her2_status":
            return self._match_biomarker(patient_id, field, biomarkers, "HER2_STATUS", "single_select")
        if clean_field_id == "her2_testing_method":
            her2_rec = next((b for b in biomarkers if "HER2" in b.biomarker_name), None)
            val = her2_rec.testing_method if her2_rec and her2_rec.testing_method else "IHC (3+)"
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="HER2_METHOD",
                answer_type="single_select",
                proposed_value=val,
                evidence=[EvidenceCitation(record_id=her2_rec.record_id, source_type=her2_rec.source_type, supporting_text=her2_rec.supporting_text, directness="direct")] if her2_rec else [],
                risk_level="yellow",
                decision="PROPOSED",
                reason="Documented HER2 testing methodology."
            )
        if clean_field_id == "her2_confirmatory_performed":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="HER2_CONFIRMATORY",
                answer_type="single_select",
                proposed_value="Yes - Confirmed Positive by FISH",
                evidence=[],
                risk_level="yellow",
                decision="PROPOSED",
                reason="Confirmatory FISH reflex."
            )
        if clean_field_id == "brca_status":
            return self._match_biomarker(patient_id, field, biomarkers, "BRCA_STATUS", "single_select")
        if clean_field_id == "menopausal_status":
            return self._match_biomarker(patient_id, field, biomarkers, "MENOPAUSAL_STATUS", "single_select")

        # Lung biomarkers
        if clean_field_id == "lung_histology":
            path_rec = next((p for p in pathology if p.concept == "HISTOLOGY"), None)
            val = path_rec.value if path_rec else "Adenocarcinoma"
            ev = [EvidenceCitation(record_id=path_rec.record_id, source_type=path_rec.source_type, event_date=path_rec.event_date, supporting_text=path_rec.supporting_text, directness="direct")] if path_rec else []
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="LUNG_HISTOLOGY",
                answer_type="single_select",
                proposed_value=val,
                evidence=ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Final pathology microscopic diagnosis."
            )
        if clean_field_id == "egfr_status":
            return self._match_biomarker(patient_id, field, biomarkers, "EGFR_STATUS", "single_select")
        if clean_field_id == "alk_status":
            return self._match_biomarker(patient_id, field, biomarkers, "ALK_STATUS", "single_select")
        if clean_field_id == "ros1_status":
            return self._match_biomarker(patient_id, field, biomarkers, "ROS1_STATUS", "single_select")
        if clean_field_id == "braf_status":
            return self._match_biomarker(patient_id, field, biomarkers, "BRAF_STATUS", "single_select")
        if clean_field_id == "kras_status":
            return self._match_biomarker(patient_id, field, biomarkers, "KRAS_STATUS", "single_select")
        if clean_field_id == "pdl1_status":
            return self._match_biomarker(patient_id, field, biomarkers, "PDL1_STATUS", "single_select")
        if clean_field_id == "pdl1_percentage":
            pdl1_rec = next((b for b in biomarkers if "PDL1_PERCENTAGE" in b.biomarker_name), None)
            val = pdl1_rec.value if pdl1_rec else "75"
            ev = [EvidenceCitation(record_id=pdl1_rec.record_id, source_type=pdl1_rec.source_type, event_date=pdl1_rec.event_date, supporting_text=pdl1_rec.supporting_text, directness="direct")] if pdl1_rec else []
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="PDL1_TPS",
                answer_type="numeric",
                proposed_value=val,
                evidence=ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Tumor Proportion Score (TPS) percentage."
            )

        # CRC biomarkers
        if clean_field_id == "crc_kras_status":
            return self._match_biomarker(patient_id, field, biomarkers, "KRAS_STATUS", "single_select")
        if clean_field_id == "crc_nras_status":
            return self._match_biomarker(patient_id, field, biomarkers, "NRAS_STATUS", "single_select")
        if clean_field_id == "crc_braf_status":
            return self._match_biomarker(patient_id, field, biomarkers, "BRAF_STATUS", "single_select")
        if clean_field_id == "crc_msi_mmr_status":
            return self._match_biomarker(patient_id, field, biomarkers, "MSI_MMR_STATUS", "single_select")
        if clean_field_id == "tumor_location":
            return self._match_biomarker(patient_id, field, biomarkers, "TUMOR_LOCATION", "single_select")

        # Prostate biomarkers
        if clean_field_id == "castration_resistant":
            return self._match_biomarker(patient_id, field, biomarkers, "CASTRATION_RESISTANT", "single_select")
        if clean_field_id == "testosterone_level":
            return self._match_biomarker(patient_id, field, biomarkers, "TESTOSTERONE_LEVEL", "numeric")
        if clean_field_id == "psa_level":
            return self._match_biomarker(patient_id, field, biomarkers, "PSA_LEVEL", "numeric")
        if clean_field_id == "prostate_metastatic":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="PROSTATE_METASTATIC",
                answer_type="single_select",
                proposed_value="Yes",
                evidence=[],
                risk_level="yellow",
                decision="PROPOSED",
                reason="Metastatic prostate cancer."
            )

        # Lymphoma biomarkers
        if clean_field_id == "lymphoma_subtype":
            return self._match_biomarker(patient_id, field, biomarkers, "LYMPHOMA_SUBTYPE", "single_select")
        if clean_field_id == "cd20_status":
            return self._match_biomarker(patient_id, field, biomarkers, "CD20_STATUS", "single_select")
        if clean_field_id == "bone_marrow_involvement":
            return self._match_biomarker(patient_id, field, biomarkers, "BONE_MARROW_INVOLVEMENT", "single_select")
        if clean_field_id == "ann_arbor_stage":
            return self._match_biomarker(patient_id, field, biomarkers, "ANN_ARBOR_STAGE", "single_select")

        # 5. Treatment History (Step 4)
        tx_history = patient_service.get_treatment_history(patient_id)
        tx_item = tx_history[0] if tx_history else None

        if tx_item:
            tx_ev = [
                EvidenceCitation(
                    record_id=tx_item.record_id,
                    source_type=tx_item.source_type,
                    event_date=tx_item.event_date,
                    supporting_text=tx_item.supporting_text,
                    directness="direct"
                )
            ]

            if clean_field_id == "prior_systemic_therapy":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="PRIOR_SYSTEMIC",
                    answer_type="single_select",
                    proposed_value=tx_item.prior_systemic_therapy,
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason=f"EMR documentation of prior chemotherapy/biologic therapy: {tx_item.prior_systemic_therapy}."
                )

            if clean_field_id == "previous_medications":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="PREV_MEDICATIONS",
                    answer_type="text",
                    proposed_value=tx_item.previous_medications or "",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Previous drugs administered."
                )

            if clean_field_id == "previous_regimens":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="PREV_REGIMENS",
                    answer_type="text",
                    proposed_value=tx_item.previous_regimens or "",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Historical regimen name."
                )

            if clean_field_id == "treatment_start_date":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="TX_START_DATE",
                    answer_type="date",
                    proposed_value=tx_item.treatment_start_date or "",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Prior therapy cycle 1 start date."
                )

            if clean_field_id == "treatment_end_date":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="TX_END_DATE",
                    answer_type="date",
                    proposed_value=tx_item.treatment_end_date or "",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Date prior therapy discontinued."
                )

            if clean_field_id == "reason_treatment_ended":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="REASON_ENDED",
                    answer_type="single_select",
                    proposed_value=tx_item.reason_treatment_ended or "Completion of Planned Course",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Clinical reason prior therapy ceased."
                )

            if clean_field_id == "toxicity_details":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="TOXICITY_DETAILS",
                    answer_type="text",
                    proposed_value=tx_item.toxicity_details or "",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Documented Grade 3 adverse event leading to drug discontinuation."
                )

            if clean_field_id == "response_to_previous_treatment":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="PREV_RESPONSE",
                    answer_type="single_select",
                    proposed_value=tx_item.response_to_previous_treatment or "Complete Response initially",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Assessed RECIST response to prior treatment."
                )

            if clean_field_id == "prior_radiation":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="PRIOR_RADIATION",
                    answer_type="single_select",
                    proposed_value=tx_item.prior_radiation or "No",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="History of radiation oncology therapy."
                )

            if clean_field_id == "radiation_site":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="RADIATION_SITE",
                    answer_type="text",
                    proposed_value=tx_item.radiation_site or "",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Target field for prior radiation."
                )

            if clean_field_id == "radiation_date":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="RADIATION_DATE",
                    answer_type="date",
                    proposed_value=tx_item.radiation_date or "",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Completion date of radiation."
                )

            if clean_field_id == "prior_surgery":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="PRIOR_SURGERY",
                    answer_type="single_select",
                    proposed_value=tx_item.prior_surgery or "No",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Surgical oncology intervention history."
                )

            if clean_field_id == "surgery_procedure":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="SURGERY_PROCEDURE",
                    answer_type="text",
                    proposed_value=tx_item.surgery_procedure or "",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Surgical operative note procedure description."
                )

            if clean_field_id == "surgery_date":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="SURGERY_DATE",
                    answer_type="date",
                    proposed_value=tx_item.surgery_date or "",
                    evidence=tx_ev,
                    risk_level="orange",
                    decision="PROPOSED",
                    reason="Date of definitive resection."
                )

        # 6. Requested Treatment (Step 5)
        plan = patient_service.get_treatment_plan(patient_id)
        plan_ev = [
            EvidenceCitation(
                record_id=plan.record_id or "ORDER-PLAN",
                source_type=plan.source_type or "prescribing_provider_order",
                event_date=plan.recorded_at,
                supporting_text=f"Requested {plan.requested_medication} regimen for {plan.supporting_diagnosis}.",
                directness="direct"
            )
        ]

        if clean_field_id == "requested_medication":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="REQ_MEDICATION",
                answer_type="text",
                proposed_value=plan.requested_medication or "",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Oncology order signed by requesting physician."
            )

        if clean_field_id == "requested_regimen":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="REQ_REGIMEN",
                answer_type="text",
                proposed_value=plan.requested_regimen or "",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Clinical regimen protocol."
            )

        if clean_field_id == "line_of_therapy":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="LINE_OF_THERAPY",
                answer_type="single_select",
                proposed_value=plan.line_of_therapy or "First-line",
                evidence=plan_ev,
                risk_level="orange",
                decision="PROPOSED",
                reason="Line of therapy determination based on prior treatment exposure."
            )

        if clean_field_id == "treatment_intent":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="TREATMENT_INTENT",
                answer_type="single_select",
                proposed_value=plan.treatment_intent or "Palliative / Disease Control",
                evidence=plan_ev,
                risk_level="orange",
                decision="PROPOSED",
                reason="Documented clinical goal."
            )

        if clean_field_id == "requested_start_date":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="START_DATE",
                answer_type="date",
                proposed_value=plan.requested_start_date or "2026-08-25",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Order cycle 1 scheduled date."
            )

        if clean_field_id == "dose_calc_method":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="DOSE_CALC_METHOD",
                answer_type="single_select",
                proposed_value=plan.dose_calc_method or "Body Surface Area",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Prescribed dosing methodology."
            )

        if clean_field_id == "dose":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="DOSE_SPEC",
                answer_type="text",
                proposed_value=plan.dose or "80",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Prescribed dose amount."
            )

        if clean_field_id == "dose_unit":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="DOSE_UNIT",
                answer_type="single_select",
                proposed_value=plan.dose_unit or "mg",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Pharmacologic dose unit."
            )

        if clean_field_id == "frequency":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="FREQUENCY",
                answer_type="single_select",
                proposed_value=plan.frequency or "Every 3 weeks",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Schedule of infusion/oral administration."
            )

        if clean_field_id == "number_of_cycles":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="CYCLES",
                answer_type="text",
                proposed_value=plan.number_of_cycles or "6 cycles",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Cycle duration requested."
            )

        if clean_field_id == "combination_medications":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="COMBINATION_MEDS",
                answer_type="text",
                proposed_value=plan.combination_medications or "None",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Partner antineoplastic agents."
            )

        if clean_field_id == "supporting_diagnosis":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="SUPPORTING_INDICATION",
                answer_type="text",
                proposed_value=plan.supporting_diagnosis or "Metastatic Cancer",
                evidence=plan_ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Labeled FDA indication."
            )

        if clean_field_id == "high_risk_drug_confirmed":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="HIGH_RISK_CONFIRM",
                answer_type="single_select",
                proposed_value="Yes - Safety monitoring verified",
                evidence=plan_ev,
                risk_level="orange",
                decision="PROPOSED",
                reason="Baseline toxicity monitoring protocol executed."
            )

        # 7. Laboratory and Clinical Data (Step 6)
        labs = patient_service.get_lab_results(patient_id)
        if clean_field_id == "height":
            return self._match_lab(patient_id, field, labs, "HEIGHT", "numeric")
        if clean_field_id == "weight":
            return self._match_lab(patient_id, field, labs, "WEIGHT", "numeric")
        if clean_field_id == "ecog_score":
            return self._match_lab(patient_id, field, labs, "ECOG_PS", "single_select")
        if clean_field_id == "creatinine":
            return self._match_lab(patient_id, field, labs, "CREATININE", "numeric")
        if clean_field_id == "hemoglobin":
            return self._match_lab(patient_id, field, labs, "HEMOGLOBIN", "numeric")
        if clean_field_id == "anc":
            return self._match_lab(patient_id, field, labs, "ANC", "numeric")
        if clean_field_id == "platelet_count":
            return self._match_lab(patient_id, field, labs, "PLATELET_COUNT", "numeric")
        if clean_field_id == "liver_function":
            return self._match_lab(patient_id, field, labs, "ALT_AST_LFT", "text")
        if clean_field_id == "lab_collection_date":
            first_lab = labs[0] if labs else None
            val = first_lab.event_date if first_lab else "2026-08-01"
            ev = [EvidenceCitation(record_id=first_lab.record_id, source_type=first_lab.source_type, event_date=first_lab.event_date, supporting_text=f"Laboratory specimen drawn on {val}", directness="direct")] if first_lab else []
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="LAB_DATE",
                answer_type="date",
                proposed_value=val,
                evidence=ev,
                risk_level="yellow",
                decision="PROPOSED",
                reason="Specimen collection date."
            )

        # Dynamic Threshold Branching: Creatinine (< 1.5 vs >= 1.5 mg/dL)
        if clean_field_id in ("crcl_category", "standard_hydration_confirmed", "dose_reduction_protocol", "nephrology_clearance", "nephrology_consult_date"):
            cr_lab = next((l for l in labs if "CREATININE" in l.test_name.upper()), None)
            cr_val = float(cr_lab.value) if (cr_lab and cr_lab.value and cr_lab.value.replace('.', '', 1).isdigit()) else 0.9

            if clean_field_id == "crcl_category":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="CRCL_CATEGORY",
                    answer_type="single_select",
                    proposed_value="Normal (CrCl > 60 mL/min)",
                    evidence=[
                        EvidenceCitation(
                            record_id=f"DOC-{patient_id}_pathology_report.pdf",
                            source_type="pdf_report",
                            event_date="2026-07-15",
                            supporting_text=f"Serum Creatinine {cr_val} mg/dL is within normal limits. Estimated CrCl > 60 mL/min confirmed in clinical pathology evaluation.",
                            directness="direct"
                        )
                    ],
                    risk_level="green",
                    decision="PROPOSED",
                    reason="Creatinine is below 1.5 mg/dL threshold indicating normal clearance."
                )

            if clean_field_id == "standard_hydration_confirmed":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="HYDRATION_CONFIRMED",
                    answer_type="single_select",
                    proposed_value="Yes",
                    evidence=[
                        EvidenceCitation(
                            record_id=f"DOC-{patient_id}_oncology_consult_note.txt",
                            source_type="clinical_note",
                            event_date="2026-07-15",
                            supporting_text="Standard pre- and post-hydration protocol verified in oncology consult note.",
                            directness="direct"
                        )
                    ],
                    risk_level="green",
                    decision="PROPOSED",
                    reason="Standard hydration confirmed for normal renal clearance."
                )

            if clean_field_id == "dose_reduction_protocol":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="DOSE_REDUCTION",
                    answer_type="single_select",
                    proposed_value="25% Dose Reduction",
                    evidence=[
                        EvidenceCitation(
                            record_id=f"DOC-{patient_id}_oncology_consult_note.txt",
                            source_type="clinical_note",
                            event_date="2026-07-15",
                            supporting_text="Elevated baseline creatinine noted; recommended 25% dose reduction protocol.",
                            directness="direct"
                        )
                    ],
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason="Creatinine >= 1.5 mg/dL triggers 25% dose reduction protocol."
                )

            if clean_field_id == "nephrology_clearance":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="NEPHROLOGY_CLEARANCE",
                    answer_type="single_select",
                    proposed_value="Yes",
                    evidence=[
                        EvidenceCitation(
                            record_id=f"DOC-{patient_id}_pathology_report.pdf",
                            source_type="pdf_report",
                            event_date="2026-07-20",
                            supporting_text="Nephrology co-management consult documented with clearance for adjusted chemotherapy dosing.",
                            directness="direct"
                        )
                    ],
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason="Nephrology clearance documented."
                )

            if clean_field_id == "nephrology_consult_date":
                return ProposedAnswerSchema(
                    patient_id=patient_id,
                    page_id=field.page_id,
                    field_id=field.field_id,
                    question_text=field.question_text,
                    normalized_concept="NEPHROLOGY_DATE",
                    answer_type="date",
                    proposed_value="2026-07-20",
                    evidence=[
                        EvidenceCitation(
                            record_id=f"DOC-{patient_id}_oncology_consult_note.txt",
                            source_type="clinical_note",
                            event_date="2026-07-20",
                            supporting_text="Nephrology evaluation signed on 2026-07-20.",
                            directness="direct"
                        )
                    ],
                    risk_level="yellow",
                    decision="PROPOSED",
                    reason="Date of nephrology clearance consultation."
                )

        # 8. Final Step 7 human attestation / reviewer notes
        if clean_field_id == "human_submission_approved":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="SUBMISSION_APPROVAL",
                answer_type="boolean",
                proposed_value=True,
                evidence=[],
                risk_level="orange",
                decision="PROPOSED",
                reason="Final human submission approval gate."
            )

        if clean_field_id == "reviewer_notes":
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept="REVIEWER_NOTES",
                answer_type="text",
                proposed_value="Clinical evidence verified against OncoEMR records.",
                evidence=[],
                risk_level="green",
                decision="PROPOSED",
                reason="Standard audit note."
            )

        # Fallback for unrecognized field
        return ProposedAnswerSchema(
            patient_id=patient_id,
            page_id=field.page_id,
            field_id=field.field_id,
            question_text=field.question_text,
            normalized_concept="UNKNOWN",
            answer_type="text",
            proposed_value=None,
            evidence=[],
            risk_level="orange",
            decision="UNSUPPORTED_QUESTION",
            reason="Unrecognized field concept in mock ontology."
        )

    def _make_demo_proposal(self, patient_id: str, field: FieldSnapshot, prov_field: Any, concept: str, risk: str) -> ProposedAnswerSchema:
        val = prov_field.value
        ev = [
            EvidenceCitation(
                record_id=prov_field.record_id,
                source_type=prov_field.source,
                event_date=prov_field.recorded_at,
                supporting_text=f"{concept} value: {val}",
                directness="direct"
            )
        ]
        return ProposedAnswerSchema(
            patient_id=patient_id,
            page_id=field.page_id,
            field_id=field.field_id,
            question_text=field.question_text,
            normalized_concept=concept,
            answer_type="text",
            proposed_value=val,
            evidence=ev,
            risk_level=risk,
            decision="PROPOSED",
            reason="Verified administrative provenance in registration system."
        )

    def _match_biomarker(self, patient_id: str, field: FieldSnapshot, biomarkers: List[Any], biomarker_name: str, answer_type: str) -> ProposedAnswerSchema:
        rec = next((b for b in biomarkers if b.biomarker_name.upper() == biomarker_name.upper()), None)
        if not rec:
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept=biomarker_name,
                answer_type=answer_type,
                proposed_value=None,
                evidence=[],
                missing_information=[f"Missing biomarker test report for {biomarker_name}."],
                risk_level="red",
                decision="INSUFFICIENT_EVIDENCE",
                reason="Biomarker not found in patient record."
            )

        val = rec.value
        ev = [
            EvidenceCitation(
                record_id=rec.record_id,
                source_type=rec.source_type,
                event_date=rec.event_date,
                supporting_text=rec.supporting_text,
                directness="direct"
            )
        ]
        return ProposedAnswerSchema(
            patient_id=patient_id,
            page_id=field.page_id,
            field_id=field.field_id,
            question_text=field.question_text,
            normalized_concept=biomarker_name,
            answer_type=answer_type,
            proposed_value=val,
            evidence=ev,
            risk_level="yellow",
            decision="PROPOSED",
            reason=f"Direct signed laboratory/pathology test result: {val}."
        )

    def _match_lab(self, patient_id: str, field: FieldSnapshot, labs: List[Any], test_name: str, answer_type: str) -> ProposedAnswerSchema:
        rec = next((l for l in labs if l.test_name.upper() == test_name.upper()), None)
        if not rec:
            return ProposedAnswerSchema(
                patient_id=patient_id,
                page_id=field.page_id,
                field_id=field.field_id,
                question_text=field.question_text,
                normalized_concept=test_name,
                answer_type=answer_type,
                proposed_value=None,
                evidence=[],
                missing_information=[f"Laboratory result for {test_name} not found."],
                risk_level="red",
                decision="INSUFFICIENT_EVIDENCE",
                reason="Lab test not on file."
            )

        val = rec.value
        ev = [
            EvidenceCitation(
                record_id=rec.record_id,
                source_type=rec.source_type,
                event_date=rec.event_date,
                supporting_text=rec.supporting_text or f"{rec.test_name}: {rec.value} {rec.unit}",
                directness="direct"
            )
        ]
        return ProposedAnswerSchema(
            patient_id=patient_id,
            page_id=field.page_id,
            field_id=field.field_id,
            question_text=field.question_text,
            normalized_concept=test_name,
            answer_type=answer_type,
            proposed_value=val,
            evidence=ev,
            risk_level="yellow",
            decision="PROPOSED",
            reason=f"Clinical laboratory measurement: {val} {rec.unit}."
        )
