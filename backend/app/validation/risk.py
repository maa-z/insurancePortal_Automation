from typing import List, Optional
from ..schemas.ai import ProposedAnswerSchema


ADMINISTRATIVE_FIELDS = {
    "patient_id",
    "full_name",
    "date_of_birth",
    "sex",
    "address",
    "member_id",
    "insurance_plan",
    "provider_name",
    "provider_npi",
    "authorization_type",
}

DIRECT_CLINICAL_FIELDS = {
    "primary_diagnosis",
    "icd10_code",
    "diagnosis_date",
    "cancer_type",
    "height",
    "weight",
    "ecog_score",
    "creatinine",
    "hemoglobin",
    "anc",
    "platelet_count",
    "liver_function",
    "lab_collection_date",
    "er_status",
    "pr_status",
    "her2_status",
    "her2_testing_method",
    "brca_status",
    "menopausal_status",
    "lung_histology",
    "egfr_status",
    "alk_status",
    "ros1_status",
    "braf_status",
    "kras_status",
    "pdl1_status",
    "pdl1_percentage",
    "crc_kras_status",
    "crc_nras_status",
    "crc_braf_status",
    "crc_msi_mmr_status",
    "tumor_location",
    "castration_resistant",
    "testosterone_level",
    "psa_level",
    "prostate_metastatic",
    "lymphoma_subtype",
    "cd20_status",
    "bone_marrow_involvement",
    "ann_arbor_stage",
}

COMPLEX_CLINICAL_FIELDS = {
    "disease_stage",
    "is_metastatic",
    "metastasis_sites",
    "is_recurrent",
    "prior_systemic_therapy",
    "previous_medications",
    "previous_regimens",
    "reason_treatment_ended",
    "toxicity_details",
    "response_to_previous_treatment",
    "line_of_therapy",
    "treatment_intent",
    "requested_medication",
    "requested_regimen",
    "dose_calc_method",
    "high_risk_drug_confirmed",
}


def classify_field_risk(
    field_id: str,
    has_conflicts: bool = False,
    has_missing_info: bool = False,
    is_identity_mismatch: bool = False,
    is_outdated_lab: bool = False,
    directness: str = "direct"
) -> str:
    """
    Returns risk level string: 'green', 'yellow', 'orange', 'red'
    """
    # Red: conflicts, missing info, identity mismatch, outdated lab
    if is_identity_mismatch or has_conflicts or has_missing_info or is_outdated_lab:
        return "red"

    clean_id = field_id.lower().replace("-", "_")

    # Green: Administrative demographics & identifiers
    if clean_id in ADMINISTRATIVE_FIELDS:
        return "green"

    # Orange: Inferred clinical fields, prior therapy history, stage inferences
    if clean_id in COMPLEX_CLINICAL_FIELDS or directness == "inferred":
        return "orange"

    # Yellow: Direct clinical laboratory & pathology measurements
    if clean_id in DIRECT_CLINICAL_FIELDS:
        return "yellow"

    return "orange"
