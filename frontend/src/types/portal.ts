export type CancerType =
  | 'Breast Cancer'
  | 'Lung Cancer'
  | 'Colorectal Cancer'
  | 'Prostate Cancer'
  | 'Lymphoma'
  | '';

export interface PortalFormData {
  // Step 1: Patient and insurance info
  patient_id: string;
  full_name: string;
  date_of_birth: string;
  sex: string;
  address: string;
  member_id: string;
  insurance_plan: string;
  provider_name: string;
  provider_npi: string;
  authorization_type: string;

  // Step 2: Diagnosis
  cancer_type: CancerType;
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
  evidence_source?: string;
  performance_status: string;

  // Step 3: Biomarkers & Pathology
  // Breast
  er_status?: string;
  pr_status?: string;
  her2_status?: string;
  her2_testing_method?: string;
  her2_confirmatory_performed?: string;
  brca_status?: string;
  menopausal_status?: string;
  // Lung
  lung_histology?: string;
  egfr_status?: string;
  alk_status?: string;
  ros1_status?: string;
  braf_status?: string;
  kras_status?: string;
  pdl1_status?: string;
  pdl1_percentage?: string;
  // Colorectal
  crc_kras_status?: string;
  crc_nras_status?: string;
  crc_braf_status?: string;
  crc_msi_mmr_status?: string;
  tumor_location?: string;
  // Prostate
  castration_resistant?: string;
  testosterone_level?: string;
  psa_level?: string;
  prostate_metastatic?: string;
  // Lymphoma
  lymphoma_subtype?: string;
  cd20_status?: string;
  bone_marrow_involvement?: string;
  ann_arbor_stage?: string;

  // Step 4: Treatment History
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
  prior_adverse_reactions?: string;

  // Step 5: Requested Treatment
  requested_medication: string;
  requested_regimen: string;
  line_of_therapy: string;
  treatment_intent: string;
  requested_start_date: string;
  dose: string;
  dose_unit: string;
  frequency: string;
  number_of_cycles: string;
  combination_medications?: string;
  supporting_diagnosis: string;
  dose_calc_method?: string;
  high_risk_drug_confirmed?: string;

  // Step 6: Laboratory & Clinical Data
  height: string;
  weight: string;
  ecog_score: string;
  creatinine: string;
  // Dynamic threshold-based branching (< 1.5 vs >= 1.5 mg/dL)
  crcl_category?: string;
  standard_hydration_confirmed?: string;
  dose_reduction_protocol?: string;
  nephrology_clearance?: string;
  nephrology_consult_date?: string;
  hemoglobin: string;
  anc: string;
  platelet_count: string;
  liver_function: string;
  lab_collection_date: string;

  // Step 7: Review & Submission Approval
  human_submission_approved: boolean;
  reviewer_notes?: string;
}

export type PortalOutcomeType = 'VERIFIED' | 'CANCELLED' | 'IN_INSPECTION';

export interface PortalSubmissionOutcome {
  outcome: PortalOutcomeType;
  confirmation_number: string;
  timestamp: string;
  summary: string;
  outstanding_review_reasons: string[];
}
