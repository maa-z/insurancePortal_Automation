import React from 'react';
import { AutomationRun, WorkflowState } from '../types/agent';
import { StatCard } from '../components/StatCard';

interface WorkflowStatusBannerProps {
  run: AutomationRun | null;
}

export const WorkflowStatusBanner: React.FC<WorkflowStatusBannerProps> = ({ run }) => {
  if (!run) {
    return (
      <div className="agent-status-banner idle" data-testid="agent-status-banner-idle">
        <div className="status-indicator-circle gray" />
        <div>
          <h4 className="banner-status-title">Agent System Standby</h4>
          <p className="banner-status-desc">Select a target patient ID and click &ldquo;Start Automation&rdquo; to launch closed-loop browser execution.</p>
        </div>
      </div>
    );
  }

  const getStateVariant = (state: WorkflowState) => {
    switch (state) {
      case 'OUTCOME_CAPTURED':
      case 'PAGE_COMPLETED':
        return 'success';
      case 'HUMAN_REVIEW_REQUIRED':
      case 'PAGE_REVIEW_REQUIRED':
      case 'SUBMISSION_APPROVAL_REQUIRED':
        return 'warning';
      case 'IDENTITY_REVIEW_REQUIRED':
      case 'FAILED':
      case 'CANCELLED':
        return 'danger';
      case 'PAGE_OBSERVING':
      case 'FIELDS_DISCOVERED':
      case 'EVIDENCE_RETRIEVING':
      case 'ANSWER_PROPOSING':
      case 'ANSWER_VALIDATING':
      case 'FIELD_FILLING':
      case 'FIELD_VERIFYING':
      case 'PAGE_RESCANNING':
      case 'SUBMITTING':
        return 'info';
      default:
        return 'neutral';
    }
  };

  const variant = getStateVariant(run.state);

  return (
    <div className="agent-status-container" data-testid="agent-status-container">
      <div className={`agent-status-banner ${variant}`} data-testid="agent-status-banner">
        <div className={`status-indicator-circle ${variant} animate-pulse`} />
        <div className="banner-main-text">
          <div className="banner-top-row">
            <span className="state-badge-large mono" data-testid="workflow-state-badge">
              {run.state}
            </span>
            <span className="run-id-pill mono">Run ID: {run.run_id}</span>
            <span className="run-id-pill mono">Patient: {run.patient_id}</span>
            <span className="portal-page-pill">Page: {run.current_page || 'Portal Initiating'}</span>
          </div>
          <p className="banner-status-desc">
            {run.error_message ||
              (run.state === 'HUMAN_REVIEW_REQUIRED'
                ? 'Automation paused: High-risk clinical branch, missing evidence, or conflict requires human verification.'
                : run.state === 'SUBMISSION_APPROVAL_REQUIRED'
                ? 'All portal steps verified: Explicit human clinical attestation required to authorize final submission.'
                : run.state === 'OUTCOME_CAPTURED'
                ? 'Portal execution completed. Prior authorization outcome successfully captured.'
                : 'Closed-loop automation active: Observing visible fields, retrieving patient evidence, and validating entries.')}
          </p>
        </div>
      </div>

      <div className="stats-row" data-testid="agent-stats-row">
        <StatCard
          label="Fields Discovered"
          value={run.fields_discovered_count}
          variant="info"
          icon="🔍"
          sublabel="Visible in portal DOM"
        />
        <StatCard
          label="Fields Filled & Verified"
          value={run.fields_filled_count}
          variant="success"
          icon="✓"
          sublabel="Validated against evidence"
        />
        <StatCard
          label="Awaiting Human Review"
          value={run.pending_reviews_count}
          variant={run.pending_reviews_count > 0 ? 'warning' : 'neutral'}
          icon="⚠"
          sublabel="Orange / Red risk items"
        />
        <StatCard
          label="Known Conflicts Detected"
          value={run.conflicts_count}
          variant={run.conflicts_count > 0 ? 'danger' : 'neutral'}
          icon="⚡"
          sublabel="Discordant or missing records"
        />
      </div>
    </div>
  );
};
