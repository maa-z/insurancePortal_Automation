import React, { useState } from 'react';
import { HumanReviewItem } from '../types/agent';
import { Badge } from '../components/Badge';

interface HumanReviewModalProps {
  reviewItem: HumanReviewItem;
  onSubmitDecision: (
    reviewId: string,
    decision: 'APPROVED' | 'EDITED' | 'REJECTED' | 'UNAVAILABLE',
    editedValue?: any,
    note?: string
  ) => void;
  onClose: () => void;
}

export const HumanReviewModal: React.FC<HumanReviewModalProps> = ({
  reviewItem,
  onSubmitDecision,
  onClose,
}) => {
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editedValue, setEditedValue] = useState<string>(
    typeof reviewItem.proposed_value === 'string'
      ? reviewItem.proposed_value
      : JSON.stringify(reviewItem.proposed_value || '')
  );
  const [reviewerNote, setReviewerNote] = useState<string>('');

  const handleApprove = () => {
    onSubmitDecision(reviewItem.review_id, 'APPROVED', undefined, reviewerNote);
  };

  const handleEditAndApprove = () => {
    onSubmitDecision(reviewItem.review_id, 'EDITED', editedValue, reviewerNote);
  };

  const handleReject = () => {
    onSubmitDecision(reviewItem.review_id, 'REJECTED', undefined, reviewerNote);
  };

  const handleUnavailable = () => {
    onSubmitDecision(reviewItem.review_id, 'UNAVAILABLE', undefined, reviewerNote);
  };

  return (
    <div className="modal-backdrop" data-testid="human-review-modal-backdrop">
      <div className="modal-container" data-testid="human-review-modal">
        <div className="modal-header">
          <div className="modal-title-row">
            <h3 className="modal-title">Clinical Review Required</h3>
            <Badge variant={reviewItem.risk_level as any} className="uppercase">
              Risk: {reviewItem.risk_level}
            </Badge>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          <div className="escalation-alert-banner">
            <strong>Reason for Escalation:</strong> {reviewItem.reason_for_escalation}
          </div>

          <div className="question-field-box">
            <span className="field-meta-tag mono">Field ID: {reviewItem.field_id} | Page: {reviewItem.page_id}</span>
            <h4 className="exact-question-text" data-testid="review-question-text">{reviewItem.question_text}</h4>
          </div>

          <div className="proposed-answer-section">
            <span className="section-label">AI Proposed Answer:</span>
            {!isEditing ? (
              <div className="proposed-value-display mono" data-testid="review-proposed-value">
                {String(reviewItem.proposed_value || 'None / Not Determined')}
              </div>
            ) : (
              <div className="edit-control-group">
                <input
                  type="text"
                  className="form-input mono"
                  data-testid="review-edit-input"
                  value={editedValue}
                  onChange={(e) => setEditedValue(e.target.value)}
                  placeholder="Enter corrected clinical value..."
                />
                {reviewItem.allowed_values && reviewItem.allowed_values.length > 0 && (
                  <div className="allowed-values-hint">
                    Allowed values: {reviewItem.allowed_values.join(', ')}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Supporting Evidence Citations */}
          <div className="evidence-records-section">
            <h5 className="evidence-heading">Supporting Patient Evidence Records</h5>
            {reviewItem.evidence.length === 0 ? (
              <p className="no-evidence-alert" data-testid="no-evidence-alert">
                ⚠ No direct supporting evidence found in clinical chart for this concept.
              </p>
            ) : (
              <div className="evidence-list" data-testid="review-evidence-list">
                {reviewItem.evidence.map((ev, idx) => (
                  <div key={idx} className="evidence-item-card">
                    <div className="ev-header">
                      <span className="ev-record-id mono">{ev.record_id}</span>
                      <span className="ev-source">{ev.source_type}</span>
                      {ev.event_date && <span className="ev-date">{ev.event_date}</span>}
                      <span className="ev-directness">{ev.directness}</span>
                    </div>
                    <p className="ev-text">&ldquo;{ev.supporting_text}&rdquo;</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Missing or Conflicting Information */}
          {reviewItem.conflicts.length > 0 && (
            <div className="conflict-box alert-danger" data-testid="review-conflicts-box">
              <h5>Conflicting Clinical Findings</h5>
              <ul>
                {reviewItem.conflicts.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {reviewItem.missing_information.length > 0 && (
            <div className="conflict-box alert-amber" data-testid="review-missing-box">
              <h5>Missing Required Prerequisites</h5>
              <ul>
                {reviewItem.missing_information.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Reviewer Note */}
          <div className="form-group full-width" style={{ marginTop: '1rem' }}>
            <label htmlFor="modal-reviewer-note" className="form-label">
              Audit Note (Recorded immutably in provenance trail)
            </label>
            <input
              id="modal-reviewer-note"
              data-testid="modal-reviewer-note"
              type="text"
              className="form-input"
              placeholder="e.g. Verified reflex FISH pathology signed by Dr. Lin..."
              value={reviewerNote}
              onChange={(e) => setReviewerNote(e.target.value)}
            />
          </div>
        </div>

        <div className="modal-footer">
          <div className="footer-left">
            {!isEditing ? (
              <button
                type="button"
                className="btn btn-secondary"
                data-testid="review-toggle-edit-btn"
                onClick={() => setIsEditing(true)}
              >
                ✏ Edit Proposed Answer
              </button>
            ) : (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setIsEditing(false)}
              >
                Cancel Edit
              </button>
            )}
          </div>

          <div className="footer-right">
            <button
              type="button"
              className="btn btn-ghost"
              data-testid="review-unavailable-btn"
              onClick={handleUnavailable}
            >
              Mark Unavailable
            </button>
            <button
              type="button"
              className="btn btn-danger"
              data-testid="review-reject-btn"
              onClick={handleReject}
            >
              Reject Answer
            </button>
            {isEditing ? (
              <button
                type="button"
                className="btn btn-success"
                data-testid="review-edit-approve-btn"
                onClick={handleEditAndApprove}
              >
                Save Edit & Approve
              </button>
            ) : (
              <button
                type="button"
                className="btn btn-primary"
                data-testid="review-approve-btn"
                onClick={handleApprove}
              >
                Approve Proposal
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
