import React, { useState } from 'react';

interface FinalSubmissionGateProps {
  patientId: string;
  onApprove: (approved: boolean, notes?: string) => void;
  isLoading: boolean;
}

export const FinalSubmissionGate: React.FC<FinalSubmissionGateProps> = ({
  patientId,
  onApprove,
  isLoading,
}) => {
  const [attestationChecked, setAttestationChecked] = useState<boolean>(false);
  const [reviewerNote, setReviewerNote] = useState<string>('');

  return (
    <div className="agent-card submission-gate-card" data-testid="final-submission-gate-card">
      <div className="gate-header">
        <span className="gate-icon">🔒</span>
        <div>
          <h3 className="gate-title">Human-in-the-Loop Final Submission Gate</h3>
          <p className="gate-desc">
            All portal sections have been successfully filled and verified by the automation agent.
            Under safety policy, final transmission to the insurance clearinghouse requires explicit licensed clinical sign-off.
          </p>
        </div>
      </div>

      <div className="gate-attestation-box">
        <label className="checkbox-approval-label">
          <input
            type="checkbox"
            id="gate-attestation-checkbox"
            data-testid="gate-attestation-checkbox"
            checked={attestationChecked}
            onChange={(e) => setAttestationChecked(e.target.checked)}
          />
          <span>
            <strong>Mandatory Submission Attestation:</strong> I attest that I have reviewed the prior authorization submission
            for Patient <strong className="mono">{patientId}</strong>. I verify all clinical statements are accurate and supported
            by medical documentation.
          </span>
        </label>

        <div className="form-group full-width" style={{ marginTop: '0.75rem' }}>
          <label htmlFor="gate-reviewer-note" className="form-label">Reviewer Attestation Note</label>
          <input
            id="gate-reviewer-note"
            data-testid="gate-reviewer-note"
            type="text"
            className="form-input"
            placeholder="e.g. Clinical review completed by Oncology Prior Auth Specialist..."
            value={reviewerNote}
            onChange={(e) => setReviewerNote(e.target.value)}
          />
        </div>
      </div>

      <div className="gate-actions-row">
        <button
          type="button"
          className="btn btn-danger"
          data-testid="gate-reject-btn"
          onClick={() => onApprove(false, reviewerNote)}
          disabled={isLoading}
        >
          Reject Submission
        </button>

        <button
          type="button"
          className="btn btn-success btn-large"
          id="gate-approve-btn"
          data-testid="gate-approve-button"
          onClick={() => onApprove(true, reviewerNote)}
          disabled={!attestationChecked || isLoading}
        >
          {isLoading ? 'Submitting to Portal...' : 'Approve & Submit to Insurance Portal →'}
        </button>
      </div>
    </div>
  );
};
