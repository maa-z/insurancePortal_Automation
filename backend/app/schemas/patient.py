from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class ProvenanceField(BaseModel):
    value: Any
    source: str
    record_id: str
    recorded_at: str


class PatientDemographics(BaseModel):
    full_name: ProvenanceField
    date_of_birth: ProvenanceField
    sex: ProvenanceField
    address: ProvenanceField


class PatientInsurance(BaseModel):
    member_id: ProvenanceField
    insurance_plan: ProvenanceField
    provider_name: ProvenanceField
    provider_npi: ProvenanceField
    authorization_type: ProvenanceField


class DiagnosisRecord(BaseModel):
    record_id: str
    patient_id: str
    cancer_type: str
    primary_diagnosis: str
    icd10_code: str
    diagnosis_date: str
    disease_stage: str
    is_new_diagnosis: str
    is_recurrent: str
    recurrence_date: Optional[str] = None
    previous_remission_date: Optional[str] = None
    is_metastatic: str
    metastasis_sites: Optional[List[str]] = None
    metastasis_confirmation_date: Optional[str] = None
    performance_status: str
    supporting_text: str
    source_type: str
    document_or_table: str
    section: Optional[str] = None
    event_date: str
    recorded_at: str
    extraction_quality: str = "verified"


class PathologyRecord(BaseModel):
    record_id: str
    patient_id: str
    concept: str
    value: str
    supporting_text: str
    source_type: str
    document_or_table: str
    section: Optional[str] = None
    event_date: str
    recorded_at: str
    extraction_quality: str = "verified"


class BiomarkerRecord(BaseModel):
    record_id: str
    patient_id: str
    biomarker_name: str
    value: str
    unit: Optional[str] = None
    testing_method: Optional[str] = None
    supporting_text: str
    source_type: str
    document_or_table: str
    section: Optional[str] = None
    event_date: str
    recorded_at: str
    extraction_quality: str = "verified"


class LabResultRecord(BaseModel):
    record_id: str
    patient_id: str
    test_name: str
    value: str
    unit: str
    event_date: str
    recorded_at: str
    source_type: str
    document_or_table: str
    extraction_quality: str = "verified"
    supporting_text: Optional[str] = None


class TreatmentHistoryRecord(BaseModel):
    record_id: str
    patient_id: str
    prior_systemic_therapy: str
    previous_medications: Optional[str] = None
    previous_regimens: Optional[str] = None
    treatment_start_date: Optional[str] = None
    treatment_end_date: Optional[str] = None
    reason_treatment_ended: Optional[str] = None
    toxicity_details: Optional[str] = None
    response_to_previous_treatment: Optional[str] = None
    prior_radiation: Optional[str] = None
    radiation_site: Optional[str] = None
    radiation_date: Optional[str] = None
    prior_surgery: Optional[str] = None
    surgery_procedure: Optional[str] = None
    surgery_date: Optional[str] = None
    supporting_text: str
    source_type: str
    document_or_table: str
    event_date: str
    recorded_at: str
    extraction_quality: str = "verified"


class TreatmentPlan(BaseModel):
    requested_medication: Optional[str] = None
    requested_regimen: Optional[str] = None
    line_of_therapy: Optional[str] = None
    treatment_intent: Optional[str] = None
    requested_start_date: Optional[str] = None
    dose: Optional[str] = None
    dose_unit: Optional[str] = None
    frequency: Optional[str] = None
    number_of_cycles: Optional[str] = None
    combination_medications: Optional[str] = None
    supporting_diagnosis: Optional[str] = None
    dose_calc_method: Optional[str] = None
    record_id: Optional[str] = None
    recorded_at: Optional[str] = None
    source_type: Optional[str] = None


class KnownConflict(BaseModel):
    type: str
    field: str
    description: str


class SyntheticPatientSchema(BaseModel):
    patient_id: str
    demographics: PatientDemographics
    insurance: PatientInsurance
    diagnoses: List[DiagnosisRecord] = []
    pathology: List[PathologyRecord] = []
    biomarkers: List[BiomarkerRecord] = []
    laboratory_results: List[LabResultRecord] = []
    treatment_history: List[TreatmentHistoryRecord] = []
    treatment_plan: TreatmentPlan = Field(default_factory=TreatmentPlan)
    known_conflicts: List[KnownConflict] = []
