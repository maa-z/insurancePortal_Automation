import React from 'react';
import { PortalFormData } from '../types/portal';

interface Step4Props {
  formData: PortalFormData;
  updateField: (field: keyof PortalFormData, value: any) => void;
}

export const Step4TreatmentHistory: React.FC<Step4Props> = ({ formData, updateField }) => {
  const handleSystemicChange = (val: string) => {
    updateField('prior_systemic_therapy', val);
    if (val !== 'Yes') {
      updateField('previous_medications', '');
      updateField('previous_regimens', '');
      updateField('treatment_start_date', '');
      updateField('treatment_end_date', '');
      updateField('reason_treatment_ended', '');
      updateField('toxicity_details', '');
      updateField('response_to_previous_treatment', '');
    }
  };

  const handleRadiationChange = (val: string) => {
    updateField('prior_radiation', val);
    if (val !== 'Yes') {
      updateField('radiation_site', '');
      updateField('radiation_date', '');
    }
  };

  const handleSurgeryChange = (val: string) => {
    updateField('prior_surgery', val);
    if (val !== 'Yes') {
      updateField('surgery_procedure', '');
      updateField('surgery_date', '');
    }
  };

  return (
    <div className="portal-step-container" data-page-id="treatment_history">
      <div className="step-header">
        <h2 className="step-title">Step 4: Prior Treatment History</h2>
        <p className="step-subtitle">Document previous systemic antineoplastic regimens, radiation therapy, and surgical interventions.</p>
      </div>

      <div className="form-grid">
        <div className="form-group full-width">
          <label className="form-label">
            Has the patient received previous systemic cancer therapy? <span className="req">*</span>
          </label>
          <div className="radio-group" role="radiogroup" aria-label="Has the patient received previous systemic cancer therapy?">
            {['Yes', 'No'].map((val) => (
              <label key={val} className="radio-label">
                <input
                  type="radio"
                  name="prior_systemic_therapy"
                  id={`field-prior-systemic-${val.toLowerCase()}`}
                  data-testid={`field-prior_systemic_therapy-${val.toLowerCase()}`}
                  value={val}
                  checked={formData.prior_systemic_therapy === val}
                  onChange={(e) => handleSystemicChange(e.target.value)}
                />
                {val}
              </label>
            ))}
          </div>
        </div>

        {/* Dynamic Branch: Previous Systemic Details */}
        {formData.prior_systemic_therapy === 'Yes' && (
          <div className="branch-panel full-width" data-testid="branch-systemic-details">
            <h4 className="branch-title">Prior Systemic Regimen Details</h4>
            
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="field-prev-medications" className="form-label">
                  Previous Medications Administered <span className="req">*</span>
                </label>
                <input
                  id="field-prev-medications"
                  data-testid="field-previous_medications"
                  type="text"
                  className="form-input"
                  placeholder="e.g. Doxorubicin, Cyclophosphamide, Paclitaxel"
                  value={formData.previous_medications || ''}
                  onChange={(e) => updateField('previous_medications', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-prev-regimens" className="form-label">
                  Previous Regimen Name <span className="req">*</span>
                </label>
                <input
                  id="field-prev-regimens"
                  data-testid="field-previous_regimens"
                  type="text"
                  className="form-input"
                  placeholder="e.g. AC followed by Paclitaxel (AC-T)"
                  value={formData.previous_regimens || ''}
                  onChange={(e) => updateField('previous_regimens', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-tx-start-date" className="form-label">
                  Treatment Start Date <span className="req">*</span>
                </label>
                <input
                  id="field-tx-start-date"
                  data-testid="field-treatment_start_date"
                  type="date"
                  className="form-input"
                  value={formData.treatment_start_date || ''}
                  onChange={(e) => updateField('treatment_start_date', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-tx-end-date" className="form-label">
                  Treatment End Date <span className="req">*</span>
                </label>
                <input
                  id="field-tx-end-date"
                  data-testid="field-treatment_end_date"
                  type="date"
                  className="form-input"
                  value={formData.treatment_end_date || ''}
                  onChange={(e) => updateField('treatment_end_date', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-reason-ended" className="form-label">
                  Reason Treatment Ended <span className="req">*</span>
                </label>
                <select
                  id="field-reason-ended"
                  data-testid="field-reason_treatment_ended"
                  className="form-select"
                  value={formData.reason_treatment_ended || ''}
                  onChange={(e) => {
                    updateField('reason_treatment_ended', e.target.value);
                    if (e.target.value !== 'Toxicity / Adverse Reaction') {
                      updateField('toxicity_details', '');
                    }
                  }}
                  required
                >
                  <option value="">Select Reason</option>
                  <option value="Completion of Planned Course">Completion of Planned Course</option>
                  <option value="Toxicity / Adverse Reaction">Toxicity / Adverse Reaction</option>
                  <option value="Disease progression / Resistance">Disease progression / Resistance</option>
                  <option value="Patient Choice / Lost to follow-up">Patient Choice / Lost to follow-up</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="field-response-prev" className="form-label">
                  Response to Previous Treatment <span className="req">*</span>
                </label>
                <select
                  id="field-response-prev"
                  data-testid="field-response_to_previous_treatment"
                  className="form-select"
                  value={formData.response_to_previous_treatment || ''}
                  onChange={(e) => updateField('response_to_previous_treatment', e.target.value)}
                  required
                >
                  <option value="">Select Clinical Response</option>
                  <option value="Complete Response initially">Complete Response initially</option>
                  <option value="Partial Response">Partial Response</option>
                  <option value="Stable Disease">Stable Disease</option>
                  <option value="Progression while on ADT">Progression while on ADT</option>
                  <option value="Disease Progression">Disease Progression</option>
                </select>
              </div>

              {/* Dynamic Branch: Toxicity details textarea */}
              {formData.reason_treatment_ended === 'Toxicity / Adverse Reaction' && (
                <div className="form-group full-width" data-testid="branch-toxicity-details">
                  <label htmlFor="field-toxicity-details" className="form-label">
                    Specific Toxicity Details & Grade <span className="req">*</span>
                  </label>
                  <textarea
                    id="field-toxicity-details"
                    data-testid="field-toxicity_details"
                    className="form-textarea"
                    rows={3}
                    placeholder="Describe specific adverse reaction, CTCAE grade, and management..."
                    value={formData.toxicity_details || ''}
                    onChange={(e) => updateField('toxicity_details', e.target.value)}
                    required
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Radiation Branch */}
        <div className="form-group full-width">
          <label className="form-label">
            Has the patient received prior radiation therapy? <span className="req">*</span>
          </label>
          <div className="radio-group" role="radiogroup" aria-label="Has the patient received prior radiation therapy?">
            {['Yes', 'No'].map((val) => (
              <label key={val} className="radio-label">
                <input
                  type="radio"
                  name="prior_radiation"
                  id={`field-prior-radiation-${val.toLowerCase()}`}
                  data-testid={`field-prior_radiation-${val.toLowerCase()}`}
                  value={val}
                  checked={formData.prior_radiation === val}
                  onChange={(e) => handleRadiationChange(e.target.value)}
                />
                {val}
              </label>
            ))}
          </div>
        </div>

        {formData.prior_radiation === 'Yes' && (
          <div className="branch-panel full-width" data-testid="branch-radiation-details">
            <h4 className="branch-title">Radiation Therapy Details</h4>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="field-radiation-site" className="form-label">
                  Radiation Anatomic Site <span className="req">*</span>
                </label>
                <input
                  id="field-radiation-site"
                  data-testid="field-radiation_site"
                  type="text"
                  className="form-input"
                  placeholder="e.g. Left chest wall"
                  value={formData.radiation_site || ''}
                  onChange={(e) => updateField('radiation_site', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-radiation-date" className="form-label">
                  Radiation Completion Date <span className="req">*</span>
                </label>
                <input
                  id="field-radiation-date"
                  data-testid="field-radiation_date"
                  type="date"
                  className="form-input"
                  value={formData.radiation_date || ''}
                  onChange={(e) => updateField('radiation_date', e.target.value)}
                  required
                />
              </div>
            </div>
          </div>
        )}

        {/* Surgery Branch */}
        <div className="form-group full-width">
          <label className="form-label">
            Has the patient undergone prior cancer surgery? <span className="req">*</span>
          </label>
          <div className="radio-group" role="radiogroup" aria-label="Has the patient undergone prior cancer surgery?">
            {['Yes', 'No'].map((val) => (
              <label key={val} className="radio-label">
                <input
                  type="radio"
                  name="prior_surgery"
                  id={`field-prior-surgery-${val.toLowerCase()}`}
                  data-testid={`field-prior_surgery-${val.toLowerCase()}`}
                  value={val}
                  checked={formData.prior_surgery === val}
                  onChange={(e) => handleSurgeryChange(e.target.value)}
                />
                {val}
              </label>
            ))}
          </div>
        </div>

        {formData.prior_surgery === 'Yes' && (
          <div className="branch-panel full-width" data-testid="branch-surgery-details">
            <h4 className="branch-title">Surgical Procedure Details</h4>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="field-surgery-procedure" className="form-label">
                  Surgical Procedure Name <span className="req">*</span>
                </label>
                <input
                  id="field-surgery-procedure"
                  data-testid="field-surgery_procedure"
                  type="text"
                  className="form-input"
                  placeholder="e.g. Left Modified Radical Mastectomy"
                  value={formData.surgery_procedure || ''}
                  onChange={(e) => updateField('surgery_procedure', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="field-surgery-date" className="form-label">
                  Procedure Date <span className="req">*</span>
                </label>
                <input
                  id="field-surgery-date"
                  data-testid="field-surgery_date"
                  type="date"
                  className="form-input"
                  value={formData.surgery_date || ''}
                  onChange={(e) => updateField('surgery_date', e.target.value)}
                  required
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
