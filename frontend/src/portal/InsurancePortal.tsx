import React, { useState, useMemo } from 'react';
import { PortalFormData, CancerType, PortalSubmissionOutcome } from '../types/portal';
import { Step1PatientInfo } from './Step1PatientInfo';
import { Step2Diagnosis } from './Step2Diagnosis';
import { Step3Biomarkers } from './Step3Biomarkers';
import { Step4TreatmentHistory } from './Step4TreatmentHistory';
import { Step5RequestedTreatment } from './Step5RequestedTreatment';
import { Step6LabClinical } from './Step6LabClinical';
import { Step7ReviewSubmission } from './Step7ReviewSubmission';

const INITIAL_FORM_DATA: PortalFormData = {
  // Step 1
  patient_id: '',
  full_name: '',
  date_of_birth: '',
  sex: '',
  address: '',
  member_id: '',
  insurance_plan: '',
  provider_name: '',
  provider_npi: '',
  authorization_type: '',

  // Step 2
  cancer_type: '',
  primary_diagnosis: '',
  icd10_code: '',
  diagnosis_date: '',
  disease_stage: '',
  is_new_diagnosis: 'Yes',
  is_recurrent: 'No',
  recurrence_date: '',
  previous_remission_date: '',
  is_metastatic: 'No',
  metastasis_sites: [],
  metastasis_confirmation_date: '',
  evidence_source: '',
  performance_status: '',

  // Step 3
  er_status: '',
  pr_status: '',
  her2_status: '',
  her2_testing_method: '',
  her2_confirmatory_performed: '',
  brca_status: '',
  menopausal_status: '',
  lung_histology: '',
  egfr_status: '',
  alk_status: '',
  ros1_status: '',
  braf_status: '',
  kras_status: '',
  pdl1_status: '',
  pdl1_percentage: '',
  crc_kras_status: '',
  crc_nras_status: '',
  crc_braf_status: '',
  crc_msi_mmr_status: '',
  tumor_location: '',
  castration_resistant: '',
  testosterone_level: '',
  psa_level: '',
  prostate_metastatic: '',
  lymphoma_subtype: '',
  cd20_status: '',
  bone_marrow_involvement: '',
  ann_arbor_stage: '',

  // Step 4
  prior_systemic_therapy: 'No',
  previous_medications: '',
  previous_regimens: '',
  treatment_start_date: '',
  treatment_end_date: '',
  reason_treatment_ended: '',
  toxicity_details: '',
  response_to_previous_treatment: '',
  prior_radiation: 'No',
  radiation_site: '',
  radiation_date: '',
  prior_surgery: 'No',
  surgery_procedure: '',
  surgery_date: '',

  // Step 5
  requested_medication: '',
  requested_regimen: '',
  line_of_therapy: '',
  treatment_intent: '',
  requested_start_date: '',
  dose: '',
  dose_unit: '',
  frequency: '',
  number_of_cycles: '',
  combination_medications: '',
  supporting_diagnosis: '',
  dose_calc_method: '',
  high_risk_drug_confirmed: '',

  // Step 6
  height: '',
  weight: '',
  ecog_score: '',
  creatinine: '',
  hemoglobin: '',
  anc: '',
  platelet_count: '',
  liver_function: '',
  lab_collection_date: '',

  // Step 7
  human_submission_approved: false,
  reviewer_notes: '',
};

const STEP_TITLES = [
  'Patient & Insurance',
  'Diagnosis & Staging',
  'Biomarkers & Pathology',
  'Treatment History',
  'Requested Treatment',
  'Labs & Clinical',
  'Review & Submit',
];

export const InsurancePortal: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [formData, setFormData] = useState<PortalFormData>(INITIAL_FORM_DATA);
  const [outcome, setOutcome] = useState<PortalSubmissionOutcome | null>(null);

  const updateField = (field: keyof PortalFormData, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Branching Rule 3: If cancer_type changes, dependent biomarkers must be cleared!
  const handleCancerTypeChange = (newType: CancerType) => {
    setFormData((prev) => ({
      ...prev,
      cancer_type: newType,
      // Clear all Step 3 biomarkers
      er_status: '',
      pr_status: '',
      her2_status: '',
      her2_testing_method: '',
      her2_confirmatory_performed: '',
      brca_status: '',
      menopausal_status: '',
      lung_histology: '',
      egfr_status: '',
      alk_status: '',
      ros1_status: '',
      braf_status: '',
      kras_status: '',
      pdl1_status: '',
      pdl1_percentage: '',
      crc_kras_status: '',
      crc_nras_status: '',
      crc_braf_status: '',
      crc_msi_mmr_status: '',
      tumor_location: '',
      castration_resistant: '',
      testosterone_level: '',
      psa_level: '',
      prostate_metastatic: '',
      lymphoma_subtype: '',
      cd20_status: '',
      bone_marrow_involvement: '',
      ann_arbor_stage: '',
    }));
  };

  // Compute a live page version / fingerprint based on current step and branch fields
  const pageVersion = useMemo(() => {
    const raw = `${currentStep}-${formData.cancer_type}-${formData.is_metastatic}-${formData.is_recurrent}-${formData.her2_status}-${formData.pdl1_status}-${formData.prior_systemic_therapy}-${formData.reason_treatment_ended}-${formData.prior_radiation}-${formData.prior_surgery}`;
    let hash = 0;
    for (let i = 0; i < raw.length; i++) {
      hash = (hash << 5) - hash + raw.charCodeAt(i);
      hash |= 0;
    }
    return `v-${Math.abs(hash).toString(16)}`;
  }, [
    currentStep,
    formData.cancer_type,
    formData.is_metastatic,
    formData.is_recurrent,
    formData.her2_status,
    formData.pdl1_status,
    formData.prior_systemic_therapy,
    formData.reason_treatment_ended,
    formData.prior_radiation,
    formData.prior_surgery,
  ]);

  const handleNext = () => {
    if (currentStep < 7) {
      setCurrentStep((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleReset = () => {
    if (window.confirm('Reset all portal fields?')) {
      setFormData(INITIAL_FORM_DATA);
      setCurrentStep(1);
      setOutcome(null);
    }
  };

  return (
    <div className="portal-page-wrapper">
      <header className="portal-header">
        <div className="portal-header-content">
          <div className="portal-brand">
            <span className="portal-logo-icon">🏥</span>
            <div>
              <h1 className="portal-heading">CarePrior Authorization Portal</h1>
              <span className="portal-subheading">National Oncology Specialty Clearinghouse — External Portal Simulation</span>
            </div>
          </div>
          <div className="portal-meta-badges">
            <span className="badge badge-neutral" data-testid="portal-step-indicator">
              Step {currentStep} of 7: {STEP_TITLES[currentStep - 1]}
            </span>
            <span className="badge badge-outline mono" data-testid="page-version-badge">
              Version: {pageVersion}
            </span>
          </div>
        </div>
      </header>

      {/* Step Progress Bar */}
      <nav className="portal-stepper" aria-label="Portal Steps">
        {STEP_TITLES.map((title, idx) => {
          const stepNum = idx + 1;
          const isActive = stepNum === currentStep;
          const isCompleted = stepNum < currentStep;
          return (
            <div
              key={stepNum}
              className={`stepper-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
              data-testid={`stepper-step-${stepNum}`}
            >
              <div className="stepper-circle">{isCompleted ? '✓' : stepNum}</div>
              <span className="stepper-label">{title}</span>
            </div>
          );
        })}
      </nav>

      <main
        className="portal-main-card"
        data-testid="portal-current-page"
        data-current-step={currentStep}
        data-page-version={pageVersion}
      >
        {currentStep === 1 && <Step1PatientInfo formData={formData} updateField={updateField} />}
        {currentStep === 2 && (
          <Step2Diagnosis
            formData={formData}
            updateField={updateField}
            onCancerTypeChange={handleCancerTypeChange}
          />
        )}
        {currentStep === 3 && <Step3Biomarkers formData={formData} updateField={updateField} />}
        {currentStep === 4 && <Step4TreatmentHistory formData={formData} updateField={updateField} />}
        {currentStep === 5 && <Step5RequestedTreatment formData={formData} updateField={updateField} />}
        {currentStep === 6 && <Step6LabClinical formData={formData} updateField={updateField} />}
        {currentStep === 7 && (
          <Step7ReviewSubmission
            formData={formData}
            updateField={updateField}
            outcome={outcome}
            setOutcome={setOutcome}
          />
        )}

        {/* Step Navigation Controls */}
        {!outcome && (
          <div className="step-navigation-bar">
            <div>
              {currentStep > 1 && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  id="portal-back-btn"
                  data-testid="portal-back-button"
                  onClick={handleBack}
                >
                  ← Back
                </button>
              )}
            </div>

            <div className="step-nav-right">
              <button
                type="button"
                className="btn btn-ghost"
                data-testid="portal-reset-button"
                onClick={handleReset}
              >
                Clear Form
              </button>
              {currentStep < 7 && (
                <button
                  type="button"
                  className="btn btn-primary"
                  id="portal-next-btn"
                  data-testid="portal-next-button"
                  onClick={handleNext}
                >
                  Continue to Step {currentStep + 1} →
                </button>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
