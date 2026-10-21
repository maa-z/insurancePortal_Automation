import React from 'react';
import { PortalFormData } from '../types/portal';

interface Step3Props {
  formData: PortalFormData;
  updateField: (field: keyof PortalFormData, value: any) => void;
}

export const Step3Biomarkers: React.FC<Step3Props> = ({ formData, updateField }) => {
  const cancerType = formData.cancer_type;

  if (!cancerType) {
    return (
      <div className="portal-step-container" data-page-id="biomarkers">
        <div className="empty-state-notice" data-testid="no-cancer-type-notice">
          <h3>No Cancer Type Selected</h3>
          <p>Please return to Step 2 and select a Cancer Type to render disease-specific biomarker questions.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="portal-step-container" data-page-id="biomarkers">
      <div className="step-header">
        <div className="step-badge">Biomarker Panel: {cancerType}</div>
        <h2 className="step-title">Step 3: Biomarkers & Molecular Pathology</h2>
        <p className="step-subtitle">
          Dynamic biomarker panel tailored strictly for <strong>{cancerType}</strong> prior authorization criteria.
        </p>
      </div>

      <div className="form-grid">
        {/* ================= BREAST CANCER ================= */}
        {cancerType === 'Breast Cancer' && (
          <>
            <div className="form-group">
              <label htmlFor="field-er-status" className="form-label">
                Estrogen Receptor (ER) Status <span className="req">*</span>
              </label>
              <select
                id="field-er-status"
                data-testid="field-er_status"
                className="form-select"
                value={formData.er_status || ''}
                onChange={(e) => updateField('er_status', e.target.value)}
                required
              >
                <option value="">Select ER Status</option>
                <option value="Positive">Positive</option>
                <option value="Negative">Negative</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-pr-status" className="form-label">
                Progesterone Receptor (PR) Status <span className="req">*</span>
              </label>
              <select
                id="field-pr-status"
                data-testid="field-pr_status"
                className="form-select"
                value={formData.pr_status || ''}
                onChange={(e) => updateField('pr_status', e.target.value)}
                required
              >
                <option value="">Select PR Status</option>
                <option value="Positive">Positive</option>
                <option value="Negative">Negative</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-her2-status" className="form-label">
                HER2 / neu Expression Status <span className="req">*</span>
              </label>
              <select
                id="field-her2-status"
                data-testid="field-her2_status"
                className="form-select"
                value={formData.her2_status || ''}
                onChange={(e) => updateField('her2_status', e.target.value)}
                required
              >
                <option value="">Select HER2 Status</option>
                <option value="Positive">Positive</option>
                <option value="Negative">Negative</option>
                <option value="Equivocal">Equivocal (IHC 2+)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-her2-method" className="form-label">
                HER2 Primary Testing Method <span className="req">*</span>
              </label>
              <select
                id="field-her2-method"
                data-testid="field-her2_testing_method"
                className="form-select"
                value={formData.her2_testing_method || ''}
                onChange={(e) => updateField('her2_testing_method', e.target.value)}
                required
              >
                <option value="">Select Method</option>
                <option value="IHC (3+)">IHC (3+)</option>
                <option value="IHC (1+)">IHC (1+)</option>
                <option value="FISH (HER2/CEP17 Ratio)">FISH (HER2/CEP17 Ratio)</option>
                <option value="NGS / CISH">NGS / CISH</option>
              </select>
            </div>

            {/* Dynamic Branch: Equivocal HER2 Confirmatory */}
            {formData.her2_status === 'Equivocal' && (
              <div className="branch-panel full-width" data-testid="branch-her2-confirmatory">
                <h4 className="branch-title">HER2 Equivocal Reflex Testing</h4>
                <div className="form-group">
                  <label htmlFor="field-her2-confirmatory" className="form-label">
                    Was confirmatory reflex FISH / ISH testing performed? <span className="req">*</span>
                  </label>
                  <select
                    id="field-her2-confirmatory"
                    data-testid="field-her2_confirmatory_performed"
                    className="form-select"
                    value={formData.her2_confirmatory_performed || ''}
                    onChange={(e) => updateField('her2_confirmatory_performed', e.target.value)}
                    required
                  >
                    <option value="">Select Confirmatory Status</option>
                    <option value="Yes - Confirmed Positive by FISH">Yes - Confirmed Positive by FISH</option>
                    <option value="Yes - Confirmed Negative by FISH">Yes - Confirmed Negative by FISH</option>
                    <option value="No - Testing Pending">No - Testing Pending</option>
                  </select>
                </div>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="field-brca-status" className="form-label">
                BRCA1 / BRCA2 Germline Mutation <span className="req">*</span>
              </label>
              <select
                id="field-brca-status"
                data-testid="field-brca_status"
                className="form-select"
                value={formData.brca_status || ''}
                onChange={(e) => updateField('brca_status', e.target.value)}
                required
              >
                <option value="">Select BRCA Status</option>
                <option value="Negative">Negative / No pathogenic variant</option>
                <option value="Positive (BRCA1 Mutation)">Positive (BRCA1 Mutation)</option>
                <option value="Positive (BRCA2 Mutation)">Positive (BRCA2 Mutation)</option>
                <option value="Unknown / Not Tested">Unknown / Not Tested</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-menopausal-status" className="form-label">
                Menopausal Status <span className="req">*</span>
              </label>
              <select
                id="field-menopausal-status"
                data-testid="field-menopausal_status"
                className="form-select"
                value={formData.menopausal_status || ''}
                onChange={(e) => updateField('menopausal_status', e.target.value)}
                required
              >
                <option value="">Select Status</option>
                <option value="Postmenopausal">Postmenopausal</option>
                <option value="Premenopausal">Premenopausal</option>
                <option value="Perimenopausal">Perimenopausal</option>
                <option value="Not Applicable">Not Applicable (Male)</option>
              </select>
            </div>
          </>
        )}

        {/* ================= LUNG CANCER ================= */}
        {cancerType === 'Lung Cancer' && (
          <>
            <div className="form-group full-width">
              <label htmlFor="field-lung-histology" className="form-label">
                Lung Histology <span className="req">*</span>
              </label>
              <select
                id="field-lung-histology"
                data-testid="field-lung_histology"
                className="form-select"
                value={formData.lung_histology || ''}
                onChange={(e) => updateField('lung_histology', e.target.value)}
                required
              >
                <option value="">Select Histology</option>
                <option value="Adenocarcinoma">Adenocarcinoma</option>
                <option value="Squamous Cell Carcinoma">Squamous Cell Carcinoma</option>
                <option value="Large Cell Neuroendocrine">Large Cell Neuroendocrine</option>
                <option value="Small Cell Lung Cancer">Small Cell Lung Cancer</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-egfr-status" className="form-label">
                EGFR Mutation Status <span className="req">*</span>
              </label>
              <select
                id="field-egfr-status"
                data-testid="field-egfr_status"
                className="form-select"
                value={formData.egfr_status || ''}
                onChange={(e) => updateField('egfr_status', e.target.value)}
                required
              >
                <option value="">Select EGFR Status</option>
                <option value="Positive (Exon 19 deletion)">Positive (Exon 19 deletion)</option>
                <option value="Positive (L858R mutation)">Positive (L858R mutation)</option>
                <option value="Positive (Other activating)">Positive (Other activating)</option>
                <option value="Negative">Negative / Wild Type</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-alk-status" className="form-label">
                ALK Rearrangement Status <span className="req">*</span>
              </label>
              <select
                id="field-alk-status"
                data-testid="field-alk_status"
                className="form-select"
                value={formData.alk_status || ''}
                onChange={(e) => updateField('alk_status', e.target.value)}
                required
              >
                <option value="">Select ALK Status</option>
                <option value="Positive">Positive (Rearrangement detected)</option>
                <option value="Negative">Negative</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-ros1-status" className="form-label">
                ROS1 Rearrangement Status <span className="req">*</span>
              </label>
              <select
                id="field-ros1-status"
                data-testid="field-ros1_status"
                className="form-select"
                value={formData.ros1_status || ''}
                onChange={(e) => updateField('ros1_status', e.target.value)}
                required
              >
                <option value="">Select ROS1 Status</option>
                <option value="Positive">Positive</option>
                <option value="Negative">Negative</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-braf-status" className="form-label">
                BRAF V600E Mutation Status <span className="req">*</span>
              </label>
              <select
                id="field-braf-status"
                data-testid="field-braf_status"
                className="form-select"
                value={formData.braf_status || ''}
                onChange={(e) => updateField('braf_status', e.target.value)}
                required
              >
                <option value="">Select BRAF Status</option>
                <option value="Positive">Positive (V600E)</option>
                <option value="Negative">Negative</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-kras-status" className="form-label">
                KRAS Mutation Status <span className="req">*</span>
              </label>
              <select
                id="field-kras-status"
                data-testid="field-kras_status"
                className="form-select"
                value={formData.kras_status || ''}
                onChange={(e) => updateField('kras_status', e.target.value)}
                required
              >
                <option value="">Select KRAS Status</option>
                <option value="Positive (G12C)">Positive (G12C)</option>
                <option value="Positive (Other)">Positive (Other)</option>
                <option value="Negative">Negative / Wild Type</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-pdl1-status" className="form-label">
                PD-L1 Expression Status <span className="req">*</span>
              </label>
              <select
                id="field-pdl1-status"
                data-testid="field-pdl1_status"
                className="form-select"
                value={formData.pdl1_status || ''}
                onChange={(e) => {
                  updateField('pdl1_status', e.target.value);
                  if (e.target.value !== 'Positive') {
                    updateField('pdl1_percentage', '');
                  }
                }}
                required
              >
                <option value="">Select PD-L1 Status</option>
                <option value="Positive">Positive (TPS ≥ 1%)</option>
                <option value="Negative">Negative (TPS &lt; 1%)</option>
                <option value="Unknown">Unknown / Not Tested</option>
              </select>
            </div>

            {/* Dynamic Branch: PD-L1 Percentage only if Positive */}
            {formData.pdl1_status === 'Positive' && (
              <div className="branch-panel full-width" data-testid="branch-pdl1-percentage">
                <h4 className="branch-title">PD-L1 Tumor Proportion Score (TPS)</h4>
                <div className="form-group">
                  <label htmlFor="field-pdl1-percentage" className="form-label">
                    PD-L1 Percentage (%) <span className="req">*</span>
                  </label>
                  <input
                    id="field-pdl1-percentage"
                    data-testid="field-pdl1_percentage"
                    type="number"
                    min="0"
                    max="100"
                    className="form-input"
                    placeholder="e.g. 75"
                    value={formData.pdl1_percentage || ''}
                    onChange={(e) => updateField('pdl1_percentage', e.target.value)}
                    required
                  />
                  <span className="field-hint">Quantified TPS between 1% and 100%</span>
                </div>
              </div>
            )}
          </>
        )}

        {/* ================= COLORECTAL CANCER ================= */}
        {cancerType === 'Colorectal Cancer' && (
          <>
            <div className="form-group">
              <label htmlFor="field-crc-kras" className="form-label">
                KRAS Status (Codons 12, 13, 61, 146) <span className="req">*</span>
              </label>
              <select
                id="field-crc-kras"
                data-testid="field-crc_kras_status"
                className="form-select"
                value={formData.crc_kras_status || ''}
                onChange={(e) => updateField('crc_kras_status', e.target.value)}
                required
              >
                <option value="">Select KRAS Status</option>
                <option value="Wild Type / Negative">Wild Type / Negative</option>
                <option value="Mutant / Positive">Mutant / Positive</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-crc-nras" className="form-label">
                NRAS Status (Codons 12, 13, 61) <span className="req">*</span>
              </label>
              <select
                id="field-crc-nras"
                data-testid="field-crc_nras_status"
                className="form-select"
                value={formData.crc_nras_status || ''}
                onChange={(e) => updateField('crc_nras_status', e.target.value)}
                required
              >
                <option value="">Select NRAS Status</option>
                <option value="Wild Type / Negative">Wild Type / Negative</option>
                <option value="Mutant / Positive">Mutant / Positive</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-crc-braf" className="form-label">
                BRAF V600E Status <span className="req">*</span>
              </label>
              <select
                id="field-crc-braf"
                data-testid="field-crc_braf_status"
                className="form-select"
                value={formData.crc_braf_status || ''}
                onChange={(e) => updateField('crc_braf_status', e.target.value)}
                required
              >
                <option value="">Select BRAF Status</option>
                <option value="Negative">Negative / Wild Type</option>
                <option value="Positive">Positive (V600E Mutation)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-crc-msi" className="form-label">
                MSI / MMR Status <span className="req">*</span>
              </label>
              <select
                id="field-crc-msi"
                data-testid="field-crc_msi_mmr_status"
                className="form-select"
                value={formData.crc_msi_mmr_status || ''}
                onChange={(e) => updateField('crc_msi_mmr_status', e.target.value)}
                required
              >
                <option value="">Select MSI / MMR Status</option>
                <option value="MSI-High / dMMR">MSI-High / dMMR (Deficient)</option>
                <option value="MSS / pMMR">MSS / pMMR (Proficient / Stable)</option>
              </select>
            </div>

            <div className="form-group full-width">
              <label htmlFor="field-tumor-location" className="form-label">
                Primary Tumor Anatomic Location <span className="req">*</span>
              </label>
              <select
                id="field-tumor-location"
                data-testid="field-tumor_location"
                className="form-select"
                value={formData.tumor_location || ''}
                onChange={(e) => updateField('tumor_location', e.target.value)}
                required
              >
                <option value="">Select Location</option>
                <option value="Left-sided (Sigmoid)">Left-sided (Sigmoid Colon)</option>
                <option value="Left-sided (Descending)">Left-sided (Descending Colon)</option>
                <option value="Right-sided (Cecum)">Right-sided (Cecum)</option>
                <option value="Right-sided (Ascending)">Right-sided (Ascending Colon)</option>
                <option value="Rectum / Rectosigmoid">Rectum / Rectosigmoid</option>
              </select>
            </div>
          </>
        )}

        {/* ================= PROSTATE CANCER ================= */}
        {cancerType === 'Prostate Cancer' && (
          <>
            <div className="form-group">
              <label htmlFor="field-castration-resistant" className="form-label">
                Castration-Resistant Status <span className="req">*</span>
              </label>
              <select
                id="field-castration-resistant"
                data-testid="field-castration_resistant"
                className="form-select"
                value={formData.castration_resistant || ''}
                onChange={(e) => updateField('castration_resistant', e.target.value)}
                required
              >
                <option value="">Select Status</option>
                <option value="Yes (mCRPC)">Yes (mCRPC - Castration Resistant)</option>
                <option value="No (CSPC)">No (Castration Sensitive)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-testosterone-level" className="form-label">
                Serum Testosterone Level (ng/dL) <span className="req">*</span>
              </label>
              <input
                id="field-testosterone-level"
                data-testid="field-testosterone_level"
                type="number"
                step="0.1"
                className="form-input"
                placeholder="e.g. 15"
                value={formData.testosterone_level || ''}
                onChange={(e) => updateField('testosterone_level', e.target.value)}
                required
              />
              <span className="field-hint">Castrate level threshold is &lt; 50 ng/dL</span>
            </div>

            <div className="form-group">
              <label htmlFor="field-psa-level" className="form-label">
                Serum PSA Level (ng/mL) <span className="req">*</span>
              </label>
              <input
                id="field-psa-level"
                data-testid="field-psa_level"
                type="number"
                step="0.1"
                className="form-input"
                placeholder="e.g. 45.2"
                value={formData.psa_level || ''}
                onChange={(e) => updateField('psa_level', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="field-prostate-metastatic" className="form-label">
                Distant Metastatic Disease Confirmed? <span className="req">*</span>
              </label>
              <select
                id="field-prostate-metastatic"
                data-testid="field-prostate_metastatic"
                className="form-select"
                value={formData.prostate_metastatic || ''}
                onChange={(e) => updateField('prostate_metastatic', e.target.value)}
                required
              >
                <option value="">Select Metastatic Status</option>
                <option value="Yes">Yes</option>
                <option value="No">No (Non-metastatic)</option>
              </select>
            </div>
          </>
        )}

        {/* ================= LYMPHOMA ================= */}
        {cancerType === 'Lymphoma' && (
          <>
            <div className="form-group full-width">
              <label htmlFor="field-lymphoma-subtype" className="form-label">
                Lymphoma Histologic Subtype <span className="req">*</span>
              </label>
              <select
                id="field-lymphoma-subtype"
                data-testid="field-lymphoma_subtype"
                className="form-select"
                value={formData.lymphoma_subtype || ''}
                onChange={(e) => updateField('lymphoma_subtype', e.target.value)}
                required
              >
                <option value="">Select Subtype</option>
                <option value="Diffuse Large B-Cell Lymphoma (DLBCL)">Diffuse Large B-Cell Lymphoma (DLBCL)</option>
                <option value="Follicular Lymphoma">Follicular Lymphoma</option>
                <option value="Mantle Cell Lymphoma">Mantle Cell Lymphoma</option>
                <option value="Hodgkin Lymphoma">Hodgkin Lymphoma</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-cd20-status" className="form-label">
                CD20 Expression Status <span className="req">*</span>
              </label>
              <select
                id="field-cd20-status"
                data-testid="field-cd20_status"
                className="form-select"
                value={formData.cd20_status || ''}
                onChange={(e) => updateField('cd20_status', e.target.value)}
                required
              >
                <option value="">Select CD20 Status</option>
                <option value="Positive">Positive</option>
                <option value="Negative">Negative</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-bone-marrow" className="form-label">
                Bone Marrow Involvement <span className="req">*</span>
              </label>
              <select
                id="field-bone-marrow"
                data-testid="field-bone_marrow_involvement"
                className="form-select"
                value={formData.bone_marrow_involvement || ''}
                onChange={(e) => updateField('bone_marrow_involvement', e.target.value)}
                required
              >
                <option value="">Select Status</option>
                <option value="No">No / Negative biopsy</option>
                <option value="Yes">Yes / Positive involvement</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="field-ann-arbor" className="form-label">
                Ann Arbor Stage <span className="req">*</span>
              </label>
              <select
                id="field-ann-arbor"
                data-testid="field-ann_arbor_stage"
                className="form-select"
                value={formData.ann_arbor_stage || ''}
                onChange={(e) => updateField('ann_arbor_stage', e.target.value)}
                required
              >
                <option value="">Select Ann Arbor Stage</option>
                <option value="Stage I">Stage I</option>
                <option value="Stage II">Stage II</option>
                <option value="Stage III">Stage III</option>
                <option value="Stage IV">Stage IV</option>
              </select>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
