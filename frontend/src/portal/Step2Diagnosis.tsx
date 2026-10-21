import React from 'react';
import { PortalFormData, CancerType } from '../types/portal';

interface Step2Props {
  formData: PortalFormData;
  updateField: (field: keyof PortalFormData, value: any) => void;
  onCancerTypeChange: (cancerType: CancerType) => void;
}

const METASTASIS_SITE_OPTIONS = [
  'Bone',
  'Liver',
  'Lung',
  'Brain',
  'Peritoneum',
  'Adrenal',
  'Pleura',
  'Other'
];

export const Step2Diagnosis: React.FC<Step2Props> = ({
  formData,
  updateField,
  onCancerTypeChange,
}) => {
  const handleSiteToggle = (site: string) => {
    const currentSites = formData.metastasis_sites || [];
    const nextSites = currentSites.includes(site)
      ? currentSites.filter((s) => s !== site)
      : [...currentSites, site];
    updateField('metastasis_sites', nextSites);
  };

  const handleMetastaticChange = (val: string) => {
    updateField('is_metastatic', val);
    if (val !== 'Yes') {
      updateField('metastasis_sites', []);
      updateField('metastasis_confirmation_date', '');
      updateField('evidence_source', '');
    }
  };

  const handleRecurrentChange = (val: string) => {
    updateField('is_recurrent', val);
    if (val !== 'Yes') {
      updateField('recurrence_date', '');
      updateField('previous_remission_date', '');
    }
  };

  return (
    <div className="portal-step-container" data-page-id="diagnosis">
      <div className="step-header">
        <h2 className="step-title">Step 2: Oncologic Diagnosis & Staging</h2>
        <p className="step-subtitle">Primary cancer classification, ICD-10 diagnostic coding, and disease extent.</p>
      </div>

      <div className="form-grid">
        <div className="form-group full-width">
          <label htmlFor="field-cancer-type" className="form-label">
            Cancer Type / Disease Domain <span className="req">*</span>
          </label>
          <select
            id="field-cancer-type"
            data-testid="field-cancer_type"
            className="form-select highlight-select"
            value={formData.cancer_type}
            onChange={(e) => onCancerTypeChange(e.target.value as CancerType)}
            required
          >
            <option value="">Select Primary Cancer Type</option>
            <option value="Breast Cancer">Breast Cancer</option>
            <option value="Lung Cancer">Lung Cancer</option>
            <option value="Colorectal Cancer">Colorectal Cancer</option>
            <option value="Prostate Cancer">Prostate Cancer</option>
            <option value="Lymphoma">Lymphoma</option>
          </select>
          <span className="field-hint">Note: Biomarker and pathology fields on Step 3 adapt to this selection.</span>
        </div>

        <div className="form-group full-width">
          <label htmlFor="field-primary-diagnosis" className="form-label">
            Primary Diagnosis Description <span className="req">*</span>
          </label>
          <input
            id="field-primary-diagnosis"
            data-testid="field-primary_diagnosis"
            type="text"
            className="form-input"
            placeholder="e.g. Malignant neoplasm of upper-outer quadrant of right female breast"
            value={formData.primary_diagnosis}
            onChange={(e) => updateField('primary_diagnosis', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-icd10-code" className="form-label">
            ICD-10-CM Diagnosis Code <span className="req">*</span>
          </label>
          <input
            id="field-icd10-code"
            data-testid="field-icd10_code"
            type="text"
            className="form-input"
            placeholder="e.g. C50.411"
            value={formData.icd10_code}
            onChange={(e) => updateField('icd10_code', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-diagnosis-date" className="form-label">
            Date of Initial Diagnosis <span className="req">*</span>
          </label>
          <input
            id="field-diagnosis-date"
            data-testid="field-diagnosis_date"
            type="date"
            className="form-input"
            value={formData.diagnosis_date}
            onChange={(e) => updateField('diagnosis_date', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-disease-stage" className="form-label">
            Clinical / Pathologic Stage <span className="req">*</span>
          </label>
          <select
            id="field-disease-stage"
            data-testid="field-disease_stage"
            className="form-select"
            value={formData.disease_stage}
            onChange={(e) => updateField('disease_stage', e.target.value)}
            required
          >
            <option value="">Select Stage</option>
            <option value="Stage 0">Stage 0</option>
            <option value="Stage I">Stage I</option>
            <option value="Stage II">Stage II</option>
            <option value="Stage IIA">Stage IIA</option>
            <option value="Stage IIB">Stage IIB</option>
            <option value="Stage III">Stage III</option>
            <option value="Stage IIIA">Stage IIIA</option>
            <option value="Stage IIIB">Stage IIIB</option>
            <option value="Stage IV">Stage IV</option>
            <option value="Stage IVA">Stage IVA</option>
            <option value="Stage IVB">Stage IVB</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="field-performance-status" className="form-label">
            Performance Status (ECOG) <span className="req">*</span>
          </label>
          <select
            id="field-performance-status"
            data-testid="field-performance_status"
            className="form-select"
            value={formData.performance_status}
            onChange={(e) => updateField('performance_status', e.target.value)}
            required
          >
            <option value="">Select ECOG Status</option>
            <option value="ECOG 0">ECOG 0 - Fully active</option>
            <option value="ECOG 1">ECOG 1 - Restricted in physically strenuous activity</option>
            <option value="ECOG 2">ECOG 2 - Ambulatory and capable of all selfcare</option>
            <option value="ECOG 3">ECOG 3 - Capable of only limited selfcare</option>
            <option value="ECOG 4">ECOG 4 - Completely disabled</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Is this a new diagnosis? <span className="req">*</span></label>
          <div className="radio-group" role="radiogroup" aria-label="Is this a new diagnosis?">
            {['Yes', 'No'].map((val) => (
              <label key={val} className="radio-label">
                <input
                  type="radio"
                  name="is_new_diagnosis"
                  id={`field-new-diag-${val.toLowerCase()}`}
                  data-testid={`field-is_new_diagnosis-${val.toLowerCase()}`}
                  value={val}
                  checked={formData.is_new_diagnosis === val}
                  onChange={(e) => updateField('is_new_diagnosis', e.target.value)}
                />
                {val}
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Is the disease recurrent? <span className="req">*</span></label>
          <div className="radio-group" role="radiogroup" aria-label="Is the disease recurrent?">
            {['Yes', 'No'].map((val) => (
              <label key={val} className="radio-label">
                <input
                  type="radio"
                  name="is_recurrent"
                  id={`field-recurrent-${val.toLowerCase()}`}
                  data-testid={`field-is_recurrent-${val.toLowerCase()}`}
                  value={val}
                  checked={formData.is_recurrent === val}
                  onChange={(e) => handleRecurrentChange(e.target.value)}
                />
                {val}
              </label>
            ))}
          </div>
        </div>

        {/* Dynamic Branch: Recurrent details */}
        {formData.is_recurrent === 'Yes' && (
          <div className="branch-panel full-width" data-testid="branch-recurrent-details">
            <h4 className="branch-title">Recurrence Information</h4>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="field-recurrence-date" className="form-label">
                  Recurrence Date <span className="req">*</span>
                </label>
                <input
                  id="field-recurrence-date"
                  data-testid="field-recurrence_date"
                  type="date"
                  className="form-input"
                  value={formData.recurrence_date || ''}
                  onChange={(e) => updateField('recurrence_date', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-remission-date" className="form-label">
                  Previous Remission Date
                </label>
                <input
                  id="field-remission-date"
                  data-testid="field-previous_remission_date"
                  type="date"
                  className="form-input"
                  value={formData.previous_remission_date || ''}
                  onChange={(e) => updateField('previous_remission_date', e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        <div className="form-group full-width">
          <label className="form-label">Is the disease metastatic? <span className="req">*</span></label>
          <div className="radio-group" role="radiogroup" aria-label="Is the disease metastatic?">
            {['Yes', 'No'].map((val) => (
              <label key={val} className="radio-label">
                <input
                  type="radio"
                  name="is_metastatic"
                  id={`field-metastatic-${val.toLowerCase()}`}
                  data-testid={`field-is_metastatic-${val.toLowerCase()}`}
                  value={val}
                  checked={formData.is_metastatic === val}
                  onChange={(e) => handleMetastaticChange(e.target.value)}
                />
                {val}
              </label>
            ))}
          </div>
        </div>

        {/* Dynamic Branch: Metastasis details */}
        {formData.is_metastatic === 'Yes' && (
          <div className="branch-panel full-width" data-testid="branch-metastatic-details">
            <h4 className="branch-title">Metastasis Documentation</h4>
            
            <div className="form-group full-width">
              <label className="form-label">
                Metastasis Sites (Select all documented sites) <span className="req">*</span>
              </label>
              <div className="checkbox-grid" data-testid="field-metastasis_sites">
                {METASTASIS_SITE_OPTIONS.map((site) => {
                  const checked = (formData.metastasis_sites || []).includes(site);
                  return (
                    <label key={site} className={`checkbox-chip ${checked ? 'selected' : ''}`}>
                      <input
                        type="checkbox"
                        id={`field-meta-site-${site.toLowerCase()}`}
                        data-testid={`field-metastasis_site-${site.toLowerCase()}`}
                        checked={checked}
                        onChange={() => handleSiteToggle(site)}
                      />
                      {site}
                    </label>
                  );
                })}
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="field-metastasis-date" className="form-label">
                  Metastatic Confirmation Date <span className="req">*</span>
                </label>
                <input
                  id="field-metastasis-date"
                  data-testid="field-metastasis_confirmation_date"
                  type="date"
                  className="form-input"
                  value={formData.metastasis_confirmation_date || ''}
                  onChange={(e) => updateField('metastasis_confirmation_date', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-evidence-source" className="form-label">
                  Metastasis Evidence Source <span className="req">*</span>
                </label>
                <select
                  id="field-evidence-source"
                  data-testid="field-evidence_source"
                  className="form-select"
                  value={formData.evidence_source || ''}
                  onChange={(e) => updateField('evidence_source', e.target.value)}
                  required
                >
                  <option value="">Select Confirmation Source</option>
                  <option value="Imaging CT / PET / MRI">Imaging CT / PET / MRI</option>
                  <option value="Biopsy / Pathology Confirmation">Biopsy / Pathology Confirmation</option>
                  <option value="Clinical Exam / Cytology">Clinical Exam / Cytology</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
