import React from 'react';
import { PortalFormData } from '../types/portal';

interface Step1Props {
  formData: PortalFormData;
  updateField: (field: keyof PortalFormData, value: any) => void;
}

export const Step1PatientInfo: React.FC<Step1Props> = ({ formData, updateField }) => {
  return (
    <div className="portal-step-container" data-page-id="patient_info">
      <div className="step-header">
        <h2 className="step-title">Step 1: Patient & Insurance Demographics</h2>
        <p className="step-subtitle">Verify patient registration identity, coverage, and requesting provider details.</p>
      </div>

      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="field-patient-id" className="form-label">
            Patient ID <span className="req">*</span>
          </label>
          <input
            id="field-patient-id"
            data-testid="field-patient_id"
            type="text"
            className="form-input"
            placeholder="e.g. P1001"
            value={formData.patient_id}
            onChange={(e) => updateField('patient_id', e.target.value)}
            required
          />
          <span className="field-hint">Master Patient Index Identifier</span>
        </div>

        <div className="form-group">
          <label htmlFor="field-full-name" className="form-label">
            Full Name <span className="req">*</span>
          </label>
          <input
            id="field-full-name"
            data-testid="field-full_name"
            type="text"
            className="form-input"
            placeholder="e.g. Eleanor Vance"
            value={formData.full_name}
            onChange={(e) => updateField('full_name', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-dob" className="form-label">
            Date of Birth <span className="req">*</span>
          </label>
          <input
            id="field-dob"
            data-testid="field-date_of_birth"
            type="date"
            className="form-input"
            value={formData.date_of_birth}
            onChange={(e) => updateField('date_of_birth', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-sex" className="form-label">
            Sex at Birth <span className="req">*</span>
          </label>
          <select
            id="field-sex"
            data-testid="field-sex"
            className="form-select"
            value={formData.sex}
            onChange={(e) => updateField('sex', e.target.value)}
            required
          >
            <option value="">Select Sex</option>
            <option value="Female">Female</option>
            <option value="Male">Male</option>
            <option value="Other">Other</option>
            <option value="Unknown">Unknown</option>
          </select>
        </div>

        <div className="form-group full-width">
          <label htmlFor="field-address" className="form-label">
            Residential Address <span className="req">*</span>
          </label>
          <input
            id="field-address"
            data-testid="field-address"
            type="text"
            className="form-input"
            placeholder="Street address, City, State, ZIP"
            value={formData.address}
            onChange={(e) => updateField('address', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-member-id" className="form-label">
            Insurance Member ID <span className="req">*</span>
          </label>
          <input
            id="field-member-id"
            data-testid="field-member_id"
            type="text"
            className="form-input"
            placeholder="e.g. MEM-889102"
            value={formData.member_id}
            onChange={(e) => updateField('member_id', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-insurance-plan" className="form-label">
            Insurance Plan / Payer <span className="req">*</span>
          </label>
          <input
            id="field-insurance-plan"
            data-testid="field-insurance_plan"
            type="text"
            className="form-input"
            placeholder="e.g. BlueCross BlueShield Comprehensive PPO"
            value={formData.insurance_plan}
            onChange={(e) => updateField('insurance_plan', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-provider-name" className="form-label">
            Requesting Provider Name <span className="req">*</span>
          </label>
          <input
            id="field-provider-name"
            data-testid="field-provider_name"
            type="text"
            className="form-input"
            placeholder="e.g. Dr. Sarah Lin, MD"
            value={formData.provider_name}
            onChange={(e) => updateField('provider_name', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="field-provider-npi" className="form-label">
            Provider NPI (10 digits) <span className="req">*</span>
          </label>
          <input
            id="field-provider-npi"
            data-testid="field-provider_npi"
            type="text"
            className="form-input"
            maxLength={10}
            placeholder="e.g. 1982736450"
            value={formData.provider_npi}
            onChange={(e) => updateField('provider_npi', e.target.value)}
            required
          />
        </div>

        <div className="form-group full-width">
          <label htmlFor="field-auth-type" className="form-label">
            Prior Authorization Type <span className="req">*</span>
          </label>
          <select
            id="field-auth-type"
            data-testid="field-authorization_type"
            className="form-select"
            value={formData.authorization_type}
            onChange={(e) => updateField('authorization_type', e.target.value)}
            required
          >
            <option value="">Select Authorization Type</option>
            <option value="Prior Authorization (Initial)">Prior Authorization (Initial)</option>
            <option value="Prior Authorization (Re-authorization/Subsequent)">Prior Authorization (Re-authorization/Subsequent)</option>
            <option value="Expedited / Urgent Prior Authorization">Expedited / Urgent Prior Authorization</option>
          </select>
        </div>
      </div>
    </div>
  );
};
