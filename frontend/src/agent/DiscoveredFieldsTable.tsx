import React from 'react';
import { DiscoveredField, ProposedAnswer, HumanReviewItem } from '../types/agent';
import { Badge } from '../components/Badge';

interface DiscoveredFieldsTableProps {
  fields: DiscoveredField[];
  proposedAnswers: Record<string, ProposedAnswer>;
  pendingReviews: HumanReviewItem[];
  onOpenReview: (review: HumanReviewItem) => void;
}

export const DiscoveredFieldsTable: React.FC<DiscoveredFieldsTableProps> = ({
  fields,
  proposedAnswers,
  pendingReviews,
  onOpenReview,
}) => {
  if (fields.length === 0) {
    return (
      <div className="agent-card discovered-fields-card" data-testid="discovered-fields-card">
        <div className="card-header">
          <h3 className="card-title">Portal DOM Observation & Field Inspection</h3>
        </div>
        <div className="empty-fields-notice">No visible fields observed yet. Start automation to inspect the portal DOM.</div>
      </div>
    );
  }

  return (
    <div className="agent-card discovered-fields-card" data-testid="discovered-fields-card">
      <div className="card-header">
        <h3 className="card-title">Observed Portal Fields ({fields.length} Visible)</h3>
        <span className="badge badge-blue">Page Fingerprint Active</span>
      </div>

      <div className="table-responsive">
        <table className="discovered-table" data-testid="discovered-fields-table">
          <thead>
            <tr>
              <th>Field Identifier</th>
              <th>Question Text</th>
              <th>Control Type</th>
              <th>Proposed Answer</th>
              <th>Risk Gate</th>
              <th>Review Status</th>
            </tr>
          </thead>
          <tbody>
            {fields.map((field) => {
              const proposal = proposedAnswers[field.field_id];
              const review = pendingReviews.find((r) => r.field_id === field.field_id);
              const risk = proposal?.risk_level || 'green';

              return (
                <tr key={field.field_id} data-testid={`discovered-field-row-${field.field_id}`}>
                  <td className="mono text-xs font-semibold">{field.field_id}</td>
                  <td className="question-col">{field.question_text}</td>
                  <td>
                    <span className="type-pill mono">{field.input_type}</span>
                  </td>
                  <td className="mono">
                    {proposal?.proposed_value !== undefined ? (
                      String(proposal.proposed_value)
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td>
                    <Badge variant={risk as any} className="uppercase text-xs">
                      {risk}
                    </Badge>
                  </td>
                  <td>
                    {review ? (
                      <button
                        type="button"
                        className="btn btn-warning btn-xs"
                        data-testid={`review-btn-${field.field_id}`}
                        onClick={() => onOpenReview(review)}
                      >
                        ⚠ Review Required
                      </button>
                    ) : proposal?.decision === 'PROPOSED' ? (
                      <span className="status-text success">✓ Safe & Filled</span>
                    ) : (
                      <span className="status-text muted">Discovered</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
