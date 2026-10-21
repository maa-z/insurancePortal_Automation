export interface ProvenanceField<T = string> {
  value: T;
  source: string;
  record_id: string;
  recorded_at: string;
}

export interface PatientDemographics {
  full_name: ProvenanceField<string>;
  date_of_birth: ProvenanceField<string>;
  sex: ProvenanceField<string>;
  address: ProvenanceField<string>;
}

export interface PatientInsurance {
  member_id: ProvenanceField<string>;
  insurance_plan: ProvenanceField<string>;
  provider_name: ProvenanceField<string>;
  provider_npi: ProvenanceField<string>;
  authorization_type: ProvenanceField<string>;
}

export interface PatientDiagnosis {
  record_id: string;
  patient_id: string;
  cancer_type: string;
  primary_diagnosis: string;
  icd10_code: string;
  diagnosis_date: string;
  disease_stage: string;
  is_new_diagnosis: string;
  is_recurrent: string;
  recurrence_date?: string;
  previous_remission_date?: string;
  is_metastatic: string;
  metastasis_sites?: string[];
  metastasis_confirmation_date?: string;
  performance_status: string;
  supporting_text: string;
  source_type: string;
  document_or_table: string;
  section: string;
  event_date: string;
  recorded_at: string;
  extraction_quality: string;
}

export interface PatientPathology {
  record_id: string;
  patient_id: string;
  concept: string;
  value: string;
  supporting_text: string;
  source_type: string;
  document_or_table: string;
  section?: string;
  event_date: string;
  recorded_at: string;
  extraction_quality: string;
}

export interface PatientBiomarker {
  record_id: string;
  patient_id: string;
  biomarker_name: string;
  value: string;
  unit?: string;
  testing_method?: string;
  supporting_text: string;
  source_type: string;
  document_or_table: string;
  section?: string;
  event_date: string;
  recorded_at: string;
  extraction_quality: string;
}

export interface PatientLabResult {
  record_id: string;
  patient_id: string;
  test_name: string;
  value: string;
  unit: string;
  event_date: string;
  recorded_at: string;
  source_type: string;
  document_or_table: string;
  extraction_quality: string;
  supporting_text?: string;
}

export interface PatientTreatmentHistoryItem {
  record_id: string;
  patient_id: string;
  prior_systemic_therapy: string;
  previous_medications?: string;
  previous_regimens?: string;
  treatment_start_date?: string;
  treatment_end_date?: string;
  reason_treatment_ended?: string;
  toxicity_details?: string;
  response_to_previous_treatment?: string;
  prior_radiation?: string;
  radiation_site?: string;
  radiation_date?: string;
  prior_surgery?: string;
  surgery_procedure?: string;
  surgery_date?: string;
  supporting_text: string;
  source_type: string;
  document_or_table: string;
  event_date: string;
  recorded_at: string;
  extraction_quality: string;
}

export interface PatientTreatmentPlan {
  requested_medication?: string;
  requested_regimen?: string;
  line_of_therapy?: string;
  treatment_intent?: string;
  requested_start_date?: string;
  dose?: string;
  dose_unit?: string;
  frequency?: string;
  number_of_cycles?: string;
  combination_medications?: string;
  supporting_diagnosis?: string;
  dose_calc_method?: string;
  record_id?: string;
  recorded_at?: string;
  source_type?: string;
}

export interface PatientKnownConflict {
  type: string;
  field: string;
  description: string;
}

export interface SyntheticPatient {
  patient_id: string;
  demographics: PatientDemographics;
  insurance: PatientInsurance;
  diagnoses: PatientDiagnosis[];
  pathology: PatientPathology[];
  biomarkers: PatientBiomarker[];
  laboratory_results: PatientLabResult[];
  treatment_history: PatientTreatmentHistoryItem[];
  treatment_plan: PatientTreatmentPlan;
  known_conflicts: PatientKnownConflict[];
}
