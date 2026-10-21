import React from 'react';
import { PortalSubmissionOutcome } from '../types/portal';

interface OutcomeCardProps {
  outcome: PortalSubmissionOutcome;
  patientId: string;
}

export const OutcomeCard: React.FC<OutcomeCardProps> = ({ outcome, patientId }) => {
  const isVerified = outcome.outcome === 'VERIFIED';
  const isCancelled = outcome.outcome === 'CANCELLED';

  return (
    <div className="agent-card outcome-card" data-testid="agent-outcome-card">
      <div className={`outcome-banner-compact ${outcome.outcome.toLowerCase()}`}>
        <div className="outcome-icon-large">
          {isVerified ? '✓' : isCancelled ? '✕' : '⚠'}
        </div>
        <div>
          <span className={`badge badge-${isVerified ? 'green' : isCancelled ? 'red' : 'yellow'} uppercase`}>
            {outcome.outcome}
          </span>
          <h3 className="outcome-headline" data-testid="agent-outcome-headline">
            {isVerified
              ? 'Prior Authorization Verified & Granted'
              : isCancelled
              ? 'Prior Authorization Cancelled'
              : 'Prior Authorization Placed In-Inspection'}
          </h3>
          <p className="outcome-desc">{outcome.summary}</p>
        </div>
      </div>

      <div className="outcome-meta-grid">
        <div className="meta-item">
          <span className="meta-label">Confirmation Number</span>
          <span className="meta-val mono" data-testid="agent-confirmation-number">{outcome.confirmation_number}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Processed At</span>
          <span className="meta-val mono">{new Date(outcome.timestamp).toLocaleTimeString()}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Patient ID</span>
          <span className="meta-val mono">{patientId}</span>
        </div>
      </div>

      {outcome.outstanding_review_reasons.length > 0 && (
        <div className="inspection-reasons-box" data-testid="agent-inspection-reasons">
          <h4 className="reasons-heading">Outstanding Reasons / Inspection Flags:</h4>
          <ul>
            {outcome.outstanding_review_reasons.map((reason, index) => (
              <li key={index} data-testid={`agent-inspection-reason-${index}`}>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
