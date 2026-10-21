import React from 'react';
import { PortalFormData } from '../types/portal';

interface Step5Props {
  formData: PortalFormData;
  updateField: (field: keyof PortalFormData, value: any) => void;
}

export const Step5RequestedTreatment: React.FC<Step5Props> = ({ formData, updateField }) => {
  const isHighRiskMed = (med: string) => {
    if (!med) return false;
    const lower = med.toLowerCase();
    return (
      lower.includes('cisplatin') ||
      lower.includes('trastuzumab') ||
      lower.includes('t-dm1') ||
      lower.includes('panitumumab') ||
      lower.includes('docetaxel') ||
      lower.includes('cetuximab') ||
      lower.includes('rituximab')
    );
  };

  const showHighRiskConfirmation = isHighRiskMed(formData.requested_medication);

  return (
    <div className="portal-step-container" data-page-id="requested_treatment">
      <div className="step-header">
        <h2 className="step-title">Step 5: Requested Oncology Treatment Plan</h2>
        <p className="step-subtitle">Specify the antineoplastic medication, regimen schedule, dosage methodology, and clinical intent.</p>
      </div>

      <div className="form-grid">
        <div className="form-group full-width">
          <label htmlFor="field-requested-medication" className="form-label">
            Requested Antineoplastic Medication(s) <span className="req">*</span>
          </label>
          <input
            id="field-requested-medication"
            data-testid="field-requested_medication"
            type="text"
            className="form-input highlight-select"
            placeholder="e.g. Trastuzumab + Pertuzumab + Docetaxel"
            value={formData.requested_medication}
            onChange={(e) => updateField('requested_medication', e.target.value)}
            required
          />
          <span className="field-hint">Include primary biologic/chemotherapy agent names</span>
        </div>

        <div className="form-group full-width">
          <label htmlFor="field-requested-regimen" className="form-label">
            Requested Clinical Regimen Protocol <span className="req">*</span>
          </label>
          <input
            id="field-requested-regimen"
            data-testid="field-requested_regimen"
            type="text"
            className="form-input"
            placeholder="e.g. THP (Docetaxel + Trastuzumab + Pertuzumab)"
            value={formData.requested_regimen}
            onChange={(e) => updateField('requested_regimen', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-line-therapy" className="form-label">
            Line of Therapy <span className="req">*</span>
          </label>
          <select
            id="field-line-therapy"
            data-testid="field-line_of_therapy"
            className="form-select"
            value={formData.line_of_therapy}
            onChange={(e) => updateField('line_of_therapy', e.target.value)}
            required
          >
            <option value="">Select Line</option>
            <option value="First-line">First-line</option>
            <option value="Second-line">Second-line</option>
            <option value="Third-line / Subsequent">Third-line / Subsequent</option>
            <option value="Neoadjuvant">Neoadjuvant</option>
            <option value="Adjuvant">Adjuvant</option>
            <option value="Maintenance">Maintenance</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="field-treatment-intent" className="form-label">
            Treatment Intent <span className="req">*</span>
          </label>
          <select
            id="field-treatment-intent"
            data-testid="field-treatment_intent"
            className="form-select"
            value={formData.treatment_intent}
            onChange={(e) => updateField('treatment_intent', e.target.value)}
            required
          >
            <option value="">Select Intent</option>
            <option value="Curative">Curative</option>
            <option value="Palliative / Disease Control">Palliative / Disease Control</option>
            <option value="Curative / Neoadjuvant">Curative / Neoadjuvant</option>
            <option value="Definitive / Concurrent Chemoradiation">Definitive / Concurrent Chemoradiation</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="field-requested-start-date" className="form-label">
            Requested Start Date <span className="req">*</span>
          </label>
          <input
            id="field-requested-start-date"
            data-testid="field-requested_start_date"
            type="date"
            className="form-input"
            value={formData.requested_start_date}
            onChange={(e) => updateField('requested_start_date', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-dose-calc-method" className="form-label">
            Dose Calculation Methodology <span className="req">*</span>
          </label>
          <select
            id="field-dose-calc-method"
            data-testid="field-dose_calc_method"
            className="form-select"
            value={formData.dose_calc_method || ''}
            onChange={(e) => updateField('dose_calc_method', e.target.value)}
            required
          >
            <option value="">Select Calculation Method</option>
            <option value="Fixed Dose">Fixed Dose</option>
            <option value="Weight-based">Weight-based (mg/kg)</option>
            <option value="Body Surface Area">Body Surface Area (mg/m2)</option>
            <option value="Body Surface Area & Weight-based">Body Surface Area & Weight-based</option>
          </select>
        </div>

        <div className="form-group full-width">
          <label htmlFor="field-dose" className="form-label">
            Dose Amount & Specification <span className="req">*</span>
          </label>
          <input
            id="field-dose"
            data-testid="field-dose"
            type="text"
            className="form-input"
            placeholder="e.g. Trastuzumab 8mg/kg loading; Docetaxel 75mg/m2 or 80"
            value={formData.dose}
            onChange={(e) => updateField('dose', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-dose-unit" className="form-label">
            Dose Unit <span className="req">*</span>
          </label>
          <select
            id="field-dose-unit"
            data-testid="field-dose_unit"
            className="form-select"
            value={formData.dose_unit}
            onChange={(e) => updateField('dose_unit', e.target.value)}
            required
          >
            <option value="">Select Dose Unit</option>
            <option value="mg">mg (Fixed)</option>
            <option value="mg/kg">mg/kg (Weight)</option>
            <option value="mg/m2">mg/m2 (BSA)</option>
            <option value="mg/kg and mg/m2">mg/kg and mg/m2 (Combination)</option>
            <option value="mg/kg and mg">mg/kg and mg</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="field-frequency" className="form-label">
            Administration Frequency <span className="req">*</span>
          </label>
          <select
            id="field-frequency"
            data-testid="field-frequency"
            className="form-select"
            value={formData.frequency}
            onChange={(e) => updateField('frequency', e.target.value)}
            required
          >
            <option value="">Select Frequency</option>
            <option value="Daily">Daily</option>
            <option value="Weekly">Weekly</option>
            <option value="Every 14 days">Every 14 days</option>
            <option value="Every 2 weeks">Every 2 weeks</option>
            <option value="Every 3 weeks">Every 3 weeks</option>
            <option value="Every 21 days">Every 21 days</option>
            <option value="Continuous">Continuous until progression</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="field-number-cycles" className="form-label">
            Number of Cycles Requested <span className="req">*</span>
          </label>
          <input
            id="field-number-cycles"
            data-testid="field-number_of_cycles"
            type="text"
            className="form-input"
            placeholder="e.g. 6 cycles or Continuous"
            value={formData.number_of_cycles}
            onChange={(e) => updateField('number_of_cycles', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-combination-meds" className="form-label">
            Combination Medications
          </label>
          <input
            id="field-combination-meds"
            data-testid="field-combination_medications"
            type="text"
            className="form-input"
            placeholder="e.g. Docetaxel or Carboplatin or None"
            value={formData.combination_medications || ''}
            onChange={(e) => updateField('combination_medications', e.target.value)}
          />
        </div>

        <div className="form-group full-width">
          <label htmlFor="field-supporting-diagnosis" className="form-label">
            Specific Clinical Supporting Indication <span className="req">*</span>
          </label>
          <input
            id="field-supporting-diagnosis"
            data-testid="field-supporting_diagnosis"
            type="text"
            className="form-input"
            placeholder="e.g. HER2+ Metastatic Breast Cancer"
            value={formData.supporting_diagnosis}
            onChange={(e) => updateField('supporting_diagnosis', e.target.value)}
            required
          />
        </div>

        {/* Dynamic Branch: High-risk confirmation question */}
        {showHighRiskConfirmation && (
          <div className="branch-panel alert-amber full-width" data-testid="branch-high-risk-confirmation">
            <h4 className="branch-title">Safety Alert: High-Risk Antineoplastic Drug Protocol</h4>
            <div className="form-group">
              <label htmlFor="field-high-risk-confirm" className="form-label">
                Has high-risk toxicity monitoring and organ function clearance been completed? <span className="req">*</span>
              </label>
              <select
                id="field-high-risk-confirm"
                data-testid="field-high_risk_drug_confirmed"
                className="form-select"
                value={formData.high_risk_drug_confirmed || ''}
                onChange={(e) => updateField('high_risk_drug_confirmed', e.target.value)}
                required
              >
                <option value="">Select Confirmation</option>
                <option value="Yes - Safety monitoring verified">Yes - Safety monitoring verified</option>
                <option value="No - Pending review">No - Pending review</option>
              </select>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
