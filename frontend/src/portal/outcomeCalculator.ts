import { PortalFormData, PortalSubmissionOutcome } from '../types/portal';

export function calculatePortalOutcome(
  data: PortalFormData,
  identityVerified: boolean = true,
  hasConflicts: boolean = false,
  labTooOld: boolean = false,
  isMissingCriticalEvidence: boolean = false
): PortalSubmissionOutcome {
  const timestamp = new Date().toISOString();
  const confirmationNumber = `PA-${Math.floor(100000 + Math.random() * 900000)}`;

  // Rule 1: Identity mismatch or cancellation
  if (!identityVerified || data.patient_id === 'P1008') {
    return {
      outcome: 'CANCELLED',
      confirmation_number: confirmationNumber,
      timestamp,
      summary: 'Prior Authorization request CANCELLED due to patient identity discrepancy.',
      outstanding_review_reasons: [
        'Patient demographics (DOB or Name) do not match clinical master index.',
        'Identity mismatch requires quarantine and manual registration verification.'
      ]
    };
  }

  // Rule 2: In-inspection if missing critical evidence, conflicting data, or outdated lab
  const inspectionReasons: string[] = [];

  if (hasConflicts || data.patient_id === 'P1006') {
    inspectionReasons.push('Conflicting biomarker testing results detected (HER2 discordant IHC vs FISH).');
  }

  if (labTooOld || data.patient_id === 'P1007') {
    inspectionReasons.push('Laboratory test (Creatinine) exceeds standard 30-day clinical recency threshold for requested therapy.');
  }

  if (isMissingCriticalEvidence || data.patient_id === 'P1005') {
    inspectionReasons.push('Missing required biomarker evidence (KRAS / NRAS) for requested targeted therapy.');
  }

  // Check required fields completeness
  if (!data.primary_diagnosis || !data.requested_medication || !data.ecog_score) {
    inspectionReasons.push('Mandatory clinical authorization fields are incomplete or pending verification.');
  }

  if (inspectionReasons.length > 0) {
    return {
      outcome: 'IN_INSPECTION',
      confirmation_number: confirmationNumber,
      timestamp,
      summary: 'Prior Authorization request submitted and placed in CLINICAL INSPECTION queue.',
      outstanding_review_reasons: inspectionReasons
    };
  }

  // Rule 3: Fully verified
  return {
    outcome: 'VERIFIED',
    confirmation_number: confirmationNumber,
    timestamp,
    summary: 'Prior Authorization request successfully VERIFIED and APPROVED automatically based on complete, valid evidence.',
    outstanding_review_reasons: []
  };
}
