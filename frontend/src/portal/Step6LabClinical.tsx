import React from 'react';
import { PortalFormData } from '../types/portal';

interface Step6Props {
  formData: PortalFormData;
  updateField: (field: keyof PortalFormData, value: any) => void;
}

export const Step6LabClinical: React.FC<Step6Props> = ({ formData, updateField }) => {
  // Check recency: if lab collection date is older than 30 days (compared to reference date 2026-08-01)
  const isLabOutdated = () => {
    if (!formData.lab_collection_date) return false;
    const labDate = new Date(formData.lab_collection_date);
    const refDate = new Date('2026-08-01');
    const diffDays = (refDate.getTime() - labDate.getTime()) / (1000 * 3600 * 24);
    return diffDays > 30;
  };

  const outdated = isLabOutdated();

  return (
    <div className="portal-step-container" data-page-id="lab_clinical">
      <div className="step-header">
        <h2 className="step-title">Step 6: Clinical Parameters & Laboratory Results</h2>
        <p className="step-subtitle">Current anthropometrics, performance status, hematology, and renal/hepatic biochemistry.</p>
      </div>

      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="field-height" className="form-label">
            Height (cm) <span className="req">*</span>
          </label>
          <input
            id="field-height"
            data-testid="field-height"
            type="number"
            step="0.1"
            className="form-input"
            placeholder="e.g. 168"
            value={formData.height}
            onChange={(e) => updateField('height', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-weight" className="form-label">
            Weight (kg) <span className="req">*</span>
          </label>
          <input
            id="field-weight"
            data-testid="field-weight"
            type="number"
            step="0.1"
            className="form-input"
            placeholder="e.g. 64.5"
            value={formData.weight}
            onChange={(e) => updateField('weight', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-ecog-score" className="form-label">
            ECOG Performance Status <span className="req">*</span>
          </label>
          <select
            id="field-ecog-score"
            data-testid="field-ecog_score"
            className="form-select"
            value={formData.ecog_score}
            onChange={(e) => updateField('ecog_score', e.target.value)}
            required
          >
            <option value="">Select ECOG Score</option>
            <option value="0">0 - Fully active, pre-disease performance</option>
            <option value="1">1 - Restricted in strenuous activity, ambulatory</option>
            <option value="2">2 - Ambulatory, capable of selfcare, up &gt;50% of waking hours</option>
            <option value="3">3 - Capable of only limited selfcare, confined to bed/chair &gt;50%</option>
            <option value="4">4 - Completely disabled, totally confined to bed/chair</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="field-lab-date" className="form-label">
            Laboratory Specimen Collection Date <span className="req">*</span>
          </label>
          <input
            id="field-lab-date"
            data-testid="field-lab_collection_date"
            type="date"
            className="form-input"
            value={formData.lab_collection_date}
            onChange={(e) => updateField('lab_collection_date', e.target.value)}
            required
          />
        </div>

        {outdated && (
          <div className="branch-panel alert-danger full-width" data-testid="outdated-lab-warning">
            <h4 className="branch-title">CRITICAL POLICY ALERT: Laboratory Results Exceed 30-Day Window</h4>
            <p>
              Specimen collection date (<strong>{formData.lab_collection_date}</strong>) is older than the required 30-day clinical recency threshold.
              Nephrotoxicity and hematologic clearance policies require repeated current laboratory draws before approval.
            </p>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="field-creatinine" className="form-label">
            Serum Creatinine (mg/dL) <span className="req">*</span>
          </label>
          <input
            id="field-creatinine"
            data-testid="field-creatinine"
            type="number"
            step="0.01"
            className="form-input"
            placeholder="e.g. 0.85"
            value={formData.creatinine}
            onChange={(e) => updateField('creatinine', e.target.value)}
            required
          />
        </div>

        {/* Dynamic Branching based on numeric threshold: Creatinine < 1.5 vs >= 1.5 mg/dL */}
        {Boolean(formData.creatinine && parseFloat(formData.creatinine) >= 1.5) && (
          <div className="branch-panel alert-warning full-width" data-testid="branch-renal-impairment">
            <h4 className="branch-title">Renal Risk Protocol (Serum Creatinine &ge; 1.5 mg/dL)</h4>
            <p className="branch-subtitle">Elevated creatinine detected. Payer policy requires nephrotoxicity mitigation and clearance documentation.</p>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="field-dose-reduction" className="form-label">
                  Chemotherapy Dose Adjustment Protocol <span className="req">*</span>
                </label>
                <select
                  id="field-dose-reduction"
                  data-testid="field-dose_reduction_protocol"
                  className="form-select"
                  value={formData.dose_reduction_protocol || ''}
                  onChange={(e) => updateField('dose_reduction_protocol', e.target.value)}
                  required
                >
                  <option value="">Select Dose Adjustment</option>
                  <option value="25% Dose Reduction">25% Dose Reduction</option>
                  <option value="50% Dose Reduction">50% Dose Reduction</option>
                  <option value="Alternative Non-Renal Regimen">Alternative Non-Renal Regimen</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Has Nephrology Clearance Been Obtained? <span className="req">*</span></label>
                <div className="radio-group" role="radiogroup">
                  {['Yes', 'No'].map((val) => (
                    <label key={val} className="radio-label">
                      <input
                        type="radio"
                        name="nephrology_clearance"
                        id={`field-nephro-clearance-${val.toLowerCase()}`}
                        data-testid={`field-nephrology_clearance-${val.toLowerCase()}`}
                        value={val}
                        checked={formData.nephrology_clearance === val}
                        onChange={(e) => updateField('nephrology_clearance', e.target.value)}
                      />
                      {val}
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="field-nephro-date" className="form-label">Nephrology Consultation Date</label>
                <input
                  id="field-nephro-date"
                  data-testid="field-nephrology_consult_date"
                  type="date"
                  className="form-input"
                  value={formData.nephrology_consult_date || ''}
                  onChange={(e) => updateField('nephrology_consult_date', e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {Boolean(formData.creatinine && parseFloat(formData.creatinine) < 1.5 && parseFloat(formData.creatinine) > 0) && (
          <div className="branch-panel full-width" data-testid="branch-normal-renal">
            <h4 className="branch-title">Standard Renal Clearance Documentation (Creatinine &lt; 1.5 mg/dL)</h4>
            <p className="branch-subtitle">Normal baseline renal function confirmed. Document standard infusion hydration parameters.</p>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="field-crcl-category" className="form-label">
                  Estimated Creatinine Clearance Category <span className="req">*</span>
                </label>
                <select
                  id="field-crcl-category"
                  data-testid="field-crcl_category"
                  className="form-select"
                  value={formData.crcl_category || ''}
                  onChange={(e) => updateField('crcl_category', e.target.value)}
                  required
                >
                  <option value="">Select Category</option>
                  <option value="Normal (CrCl > 60 mL/min)">Normal (CrCl &gt; 60 mL/min)</option>
                  <option value="Borderline (CrCl 50-60 mL/min)">Borderline (CrCl 50-60 mL/min)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Standard Pre-infusion Hydration Protocol Confirmed? <span className="req">*</span></label>
                <div className="radio-group" role="radiogroup">
                  {['Yes', 'No'].map((val) => (
                    <label key={val} className="radio-label">
                      <input
                        type="radio"
                        name="standard_hydration_confirmed"
                        id={`field-hydration-${val.toLowerCase()}`}
                        data-testid={`field-standard_hydration_confirmed-${val.toLowerCase()}`}
                        value={val}
                        checked={formData.standard_hydration_confirmed === val}
                        onChange={(e) => updateField('standard_hydration_confirmed', e.target.value)}
                      />
                      {val}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}


        <div className="form-group">
          <label htmlFor="field-hemoglobin" className="form-label">
            Hemoglobin (g/dL) <span className="req">*</span>
          </label>
          <input
            id="field-hemoglobin"
            data-testid="field-hemoglobin"
            type="number"
            step="0.1"
            className="form-input"
            placeholder="e.g. 12.4"
            value={formData.hemoglobin}
            onChange={(e) => updateField('hemoglobin', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-anc" className="form-label">
            Absolute Neutrophil Count (ANC, x10^3/uL) <span className="req">*</span>
          </label>
          <input
            id="field-anc"
            data-testid="field-anc"
            type="number"
            step="0.1"
            className="form-input"
            placeholder="e.g. 3.8"
            value={formData.anc}
            onChange={(e) => updateField('anc', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-platelets" className="form-label">
            Platelet Count (x10^3/uL) <span className="req">*</span>
          </label>
          <input
            id="field-platelets"
            data-testid="field-platelet_count"
            type="number"
            className="form-input"
            placeholder="e.g. 240"
            value={formData.platelet_count}
            onChange={(e) => updateField('platelet_count', e.target.value)}
            required
          />
        </div>

        <div className="form-group full-width">
          <label htmlFor="field-liver-function" className="form-label">
            Liver Function / Transaminases (ALT, AST, Total Bili) <span className="req">*</span>
          </label>
          <input
            id="field-liver-function"
            data-testid="field-liver_function"
            type="text"
            className="form-input"
            placeholder="e.g. Normal (ALT 22 U/L, AST 26 U/L, Total Bili 0.6 mg/dL)"
            value={formData.liver_function}
            onChange={(e) => updateField('liver_function', e.target.value)}
            required
          />
        </div>
      </div>
    </div>
  );
};
