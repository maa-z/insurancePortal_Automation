import React from 'react';
import { PortalFormData, PortalSubmissionOutcome } from '../types/portal';
import { calculatePortalOutcome } from './outcomeCalculator';

interface Step7Props {
  formData: PortalFormData;
  updateField: (field: keyof PortalFormData, value: any) => void;
  outcome: PortalSubmissionOutcome | null;
  setOutcome: (outcome: PortalSubmissionOutcome) => void;
}

export const Step7ReviewSubmission: React.FC<Step7Props> = ({
  formData,
  updateField,
  outcome,
  setOutcome,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.human_submission_approved) {
      alert('Explicit human review approval checkbox is required before submission.');
      return;
    }

    const calculatedOutcome = calculatePortalOutcome(formData);
    setOutcome(calculatedOutcome);
  };

  if (outcome) {
    const isVerified = outcome.outcome === 'VERIFIED';
    const isCancelled = outcome.outcome === 'CANCELLED';

    return (
      <div className="portal-step-container" data-page-id="submission_outcome" data-testid="portal-outcome-screen">
        <div className={`outcome-banner ${outcome.outcome.toLowerCase()}`} data-testid={`outcome-${outcome.outcome.toLowerCase()}`}>
          <div className="outcome-icon">
            {isVerified ? '✓' : isCancelled ? '✕' : '⚠'}
          </div>
          <div className="outcome-content">
            <span className="outcome-pill">{outcome.outcome}</span>
            <h2 className="outcome-title" data-testid="outcome-status-title">
              {isVerified
                ? 'Prior Authorization Approved & Verified'
                : isCancelled
                ? 'Prior Authorization Request Cancelled'
                : 'Prior Authorization Placed In-Inspection'}
            </h2>
            <p className="outcome-summary" data-testid="outcome-summary">{outcome.summary}</p>
          </div>
        </div>

        <div className="outcome-details-card">
          <div className="detail-row">
            <span className="detail-label">Confirmation Number</span>
            <span className="detail-value mono" data-testid="outcome-confirmation-number">{outcome.confirmation_number}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Submission Timestamp</span>
            <span className="detail-value mono">{new Date(outcome.timestamp).toLocaleString()}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Patient ID</span>
            <span className="detail-value">{formData.patient_id} ({formData.full_name})</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Requested Regimen</span>
            <span className="detail-value">{formData.requested_regimen || formData.requested_medication}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Requesting Provider</span>
            <span className="detail-value">{formData.provider_name} (NPI: {formData.provider_npi})</span>
          </div>

          {outcome.outstanding_review_reasons.length > 0 && (
            <div className="inspection-reasons-block" data-testid="inspection-reasons-list">
              <h4>Outstanding Inspection Reasons & Discrepancies</h4>
              <ul>
                {outcome.outstanding_review_reasons.map((r, i) => (
                  <li key={i} data-testid={`inspection-reason-${i}`}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="portal-step-container" data-page-id="review_submission">
      <div className="step-header">
        <h2 className="step-title">Step 7: Final Review & Authorization Submission</h2>
        <p className="step-subtitle">Audit all patient clinical information, biomarker matches, and dosage prior to submission.</p>
      </div>

      <div className="review-summary-grid">
        <div className="review-card">
          <h4 className="review-card-title">1. Patient & Demographics</h4>
          <p><strong>Name:</strong> {formData.full_name || '—'}</p>
          <p><strong>DOB / Sex:</strong> {formData.date_of_birth || '—'} / {formData.sex || '—'}</p>
          <p><strong>Member ID:</strong> {formData.member_id || '—'}</p>
          <p><strong>Provider:</strong> {formData.provider_name || '—'} (NPI: {formData.provider_npi || '—'})</p>
        </div>

        <div className="review-card">
          <h4 className="review-card-title">2. Diagnosis & Staging</h4>
          <p><strong>Cancer:</strong> {formData.cancer_type || '—'}</p>
          <p><strong>Primary:</strong> {formData.primary_diagnosis || '—'}</p>
          <p><strong>Stage:</strong> {formData.disease_stage || '—'} (ICD-10: {formData.icd10_code || '—'})</p>
          <p><strong>Metastatic:</strong> {formData.is_metastatic} {formData.metastasis_sites?.length ? `(${formData.metastasis_sites.join(', ')})` : ''}</p>
        </div>

        <div className="review-card">
          <h4 className="review-card-title">3. Key Biomarkers</h4>
          {formData.cancer_type === 'Breast Cancer' && (
            <>
              <p><strong>ER / PR:</strong> {formData.er_status} / {formData.pr_status}</p>
              <p><strong>HER2:</strong> {formData.her2_status} ({formData.her2_testing_method})</p>
              <p><strong>BRCA:</strong> {formData.brca_status}</p>
            </>
          )}
          {formData.cancer_type === 'Lung Cancer' && (
            <>
              <p><strong>Histology:</strong> {formData.lung_histology}</p>
              <p><strong>EGFR / ALK:</strong> {formData.egfr_status} / {formData.alk_status}</p>
              <p><strong>PD-L1:</strong> {formData.pdl1_status} {formData.pdl1_percentage ? `(${formData.pdl1_percentage}%)` : ''}</p>
            </>
          )}
          {formData.cancer_type === 'Colorectal Cancer' && (
            <>
              <p><strong>KRAS / NRAS:</strong> {formData.crc_kras_status} / {formData.crc_nras_status}</p>
              <p><strong>BRAF / MSI:</strong> {formData.crc_braf_status} / {formData.crc_msi_mmr_status}</p>
              <p><strong>Location:</strong> {formData.tumor_location}</p>
            </>
          )}
          {formData.cancer_type === 'Prostate Cancer' && (
            <>
              <p><strong>Castration Resistant:</strong> {formData.castration_resistant}</p>
              <p><strong>PSA / Testosterone:</strong> {formData.psa_level} ng/mL / {formData.testosterone_level} ng/dL</p>
            </>
          )}
          {formData.cancer_type === 'Lymphoma' && (
            <>
              <p><strong>Subtype:</strong> {formData.lymphoma_subtype}</p>
              <p><strong>CD20 / Ann Arbor:</strong> {formData.cd20_status} / {formData.ann_arbor_stage}</p>
            </>
          )}
        </div>

        <div className="review-card">
          <h4 className="review-card-title">4. Requested Regimen & Labs</h4>
          <p><strong>Drug:</strong> {formData.requested_medication || '—'}</p>
          <p><strong>Regimen:</strong> {formData.requested_regimen || '—'}</p>
          <p><strong>Dose:</strong> {formData.dose} {formData.dose_unit} ({formData.frequency})</p>
          <p><strong>Creatinine:</strong> {formData.creatinine} mg/dL (Drawn: {formData.lab_collection_date})</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="submission-approval-box" data-testid="submission-approval-box">
        <label className="checkbox-approval-label">
          <input
            type="checkbox"
            id="field-submission-approval"
            data-testid="field-human_submission_approved"
            checked={formData.human_submission_approved}
            onChange={(e) => updateField('human_submission_approved', e.target.checked)}
            required
          />
          <span>
            <strong>Required Clinical Human Attestation:</strong> I confirm that I have reviewed the clinical evidence,
            confirmed the identity of <strong>{formData.full_name || formData.patient_id}</strong>, verified all entered values,
            and hereby authorize final submission of this prior authorization request.
          </span>
        </label>

        <div className="form-group full-width" style={{ marginTop: '1rem' }}>
          <label htmlFor="field-reviewer-notes" className="form-label">Reviewer Notes (Optional)</label>
          <input
            id="field-reviewer-notes"
            data-testid="field-reviewer_notes"
            type="text"
            className="form-input"
            placeholder="Add any audit or peer notes..."
            value={formData.reviewer_notes || ''}
            onChange={(e) => updateField('reviewer_notes', e.target.value)}
          />
        </div>

        <div className="submit-action-row">
          <button
            type="submit"
            className="btn btn-primary btn-large"
            id="submit-portal-btn"
            data-testid="submit-portal-button"
            disabled={!formData.human_submission_approved}
          >
            Submit Authorization Request
          </button>
        </div>
      </form>
    </div>
  );
};
