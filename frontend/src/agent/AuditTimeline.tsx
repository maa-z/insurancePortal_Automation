import React from 'react';
import { AuditEvent } from '../types/agent';
import { Badge } from '../components/Badge';

interface AuditTimelineProps {
  events: AuditEvent[];
}

export const AuditTimeline: React.FC<AuditTimelineProps> = ({ events }) => {
  return (
    <div className="agent-card audit-timeline-card" data-testid="audit-timeline-card">
      <div className="card-header">
        <h3 className="card-title">Live Audit Trail & Provenance Timeline</h3>
        <span className="badge badge-gray">{events.length} Events Logged</span>
      </div>

      <div className="timeline-container" data-testid="timeline-events-list">
        {events.length === 0 ? (
          <div className="empty-timeline-notice">No audit events yet. Start an automation run to stream logs.</div>
        ) : (
          events.map((ev, idx) => {
            const hasError = !!ev.error;
            const hasHumanDecision = !!ev.human_decision;
            const timeStr = new Date(ev.timestamp).toLocaleTimeString();

            return (
              <div
                key={ev.event_id || idx}
                className={`timeline-item ${hasError ? 'item-error' : hasHumanDecision ? 'item-human' : ''}`}
                data-testid={`audit-event-${idx}`}
              >
                <div className="timeline-marker" />
                <div className="timeline-content">
                  <div className="timeline-header-row">
                    <span className="timeline-time mono">{timeStr}</span>
                    {ev.transition && (
                      <Badge variant="blue" className="mono">
                        {ev.transition}
                      </Badge>
                    )}
                    {ev.portal_page && <span className="timeline-page-tag">Page: {ev.portal_page}</span>}
                    {ev.risk_level && <Badge variant={ev.risk_level as any}>Risk: {ev.risk_level}</Badge>}
                  </div>

                  {ev.field_id && (
                    <div className="timeline-field-info">
                      <span className="field-id-tag mono">Field: {ev.field_id}</span>
                      {ev.question_text && <span className="question-quote">&ldquo;{ev.question_text}&rdquo;</span>}
                    </div>
                  )}

                  {ev.retrieved_evidence_ids && ev.retrieved_evidence_ids.length > 0 && (
                    <div className="timeline-evidence-row">
                      <span className="ev-tag">Evidence IDs:</span>
                      {ev.retrieved_evidence_ids.map((id, i) => (
                        <span key={i} className="evidence-pill mono">
                          {id}
                        </span>
                      ))}
                    </div>
                  )}

                  {ev.proposed_answer && (
                    <div className="timeline-proposal">
                      <strong>AI Proposal:</strong> {JSON.stringify(ev.proposed_answer)}
                    </div>
                  )}

                  {ev.filled_value !== undefined && ev.filled_value !== null && (
                    <div className="timeline-filled">
                      <span className="fill-check">✓ Verified Filled in DOM:</span> <strong className="mono">{JSON.stringify(ev.filled_value)}</strong>
                    </div>
                  )}

                  {hasHumanDecision && (
                    <div className="timeline-human-action">
                      <span className="human-icon">👤 Human Decision:</span> <strong>{ev.human_decision}</strong>
                      {ev.human_edit !== undefined && (
                        <span> (Edited Value: <strong className="mono">{String(ev.human_edit)}</strong>)</span>
                      )}
                    </div>
                  )}

                  {ev.error && (
                    <div className="timeline-error-alert alert-danger">
                      <strong>Error:</strong> {ev.error}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
