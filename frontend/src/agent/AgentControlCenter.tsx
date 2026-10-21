import React, { useState, useEffect, useRef } from 'react';
import { AutomationRun, HumanReviewItem, AuditEvent, DiscoveredField, ProposedAnswer } from '../types/agent';
import {
  startAutomationRun,
  fetchRun,
  pauseRun,
  resumeRun,
  cancelRun,
  fetchPendingReviews,
  submitReviewDecision,
  approveSubmission,
  fetchAuditTimeline,
} from '../api/client';
import { PatientSelector } from './PatientSelector';
import { WorkflowStatusBanner } from './WorkflowStatusBanner';
import { DiscoveredFieldsTable } from './DiscoveredFieldsTable';
import { HumanReviewModal } from './HumanReviewModal';
import { FinalSubmissionGate } from './FinalSubmissionGate';
import { OutcomeCard } from './OutcomeCard';
import { AuditTimeline } from './AuditTimeline';

export const AgentControlCenter: React.FC = () => {
  const [selectedPatientId, setSelectedPatientId] = useState<string>('P1001');
  const [aiMode, setAiMode] = useState<'mock' | 'llm'>('mock');
  const [activeRun, setActiveRun] = useState<AutomationRun | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [pendingReviews, setPendingReviews] = useState<HumanReviewItem[]>([]);
  const [selectedReviewModal, setSelectedReviewModal] = useState<HumanReviewItem | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [discoveredFields, setDiscoveredFields] = useState<DiscoveredField[]>([]);
  const [proposedAnswers, setProposedAnswers] = useState<Record<string, ProposedAnswer>>({});

  const sseRef = useRef<EventSource | null>(null);

  // Poll / SSE stream listener when run is active
  useEffect(() => {
    if (!activeRun?.run_id) return;

    const runId = activeRun.run_id;

    // Load initial reviews and timeline
    fetchPendingReviews(runId).then(setPendingReviews).catch(console.error);
    fetchAuditTimeline(runId).then(setAuditEvents).catch(console.error);

    // Setup SSE stream
    const eventSource = new EventSource(`/api/automation/runs/${runId}/events`);
    sseRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'STATE_CHANGE' || data.type === 'RUN_UPDATED') {
          setActiveRun(data.run);
        } else if (data.type === 'AUDIT_EVENT') {
          setAuditEvents((prev) => [data.event, ...prev]);
        } else if (data.type === 'REVIEW_REQUIRED') {
          setPendingReviews((prev) => {
            const exists = prev.some((r) => r.review_id === data.review.review_id);
            if (!exists) return [...prev, data.review];
            return prev;
          });
        } else if (data.type === 'FIELDS_DISCOVERED') {
          setDiscoveredFields(data.fields || []);
        } else if (data.type === 'ANSWER_PROPOSED') {
          setProposedAnswers((prev) => ({
            ...prev,
            [data.proposal.field_id]: data.proposal,
          }));
        } else if (data.type === 'OUTCOME_CAPTURED') {
          setActiveRun((prev) => prev ? { ...prev, state: 'OUTCOME_CAPTURED', outcome: data.outcome } : prev);
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    // Backup polling every 2.5s in case SSE drops
    const interval = setInterval(async () => {
      try {
        const updated = await fetchRun(runId);
        setActiveRun(updated);
        const reviews = await fetchPendingReviews(runId);
        setPendingReviews(reviews);

        if (['OUTCOME_CAPTURED', 'FAILED', 'CANCELLED'].includes(updated.state)) {
          clearInterval(interval);
        }
      } catch (e) {
        console.error('Polling error:', e);
      }
    }, 2500);

    return () => {
      eventSource.close();
      clearInterval(interval);
    };
  }, [activeRun?.run_id]);

  const handleStart = async () => {
    try {
      setIsLoading(true);
      setAuditEvents([]);
      setDiscoveredFields([]);
      setProposedAnswers({});
      setPendingReviews([]);
      const newRun = await startAutomationRun(selectedPatientId, aiMode);
      setActiveRun(newRun);
    } catch (err: any) {
      alert(`Failed to start run: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePause = async () => {
    if (!activeRun) return;
    try {
      setIsLoading(true);
      const updated = await pauseRun(activeRun.run_id);
      setActiveRun(updated);
    } catch (err: any) {
      alert(`Failed to pause: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResume = async () => {
    if (!activeRun) return;
    try {
      setIsLoading(true);
      const updated = await resumeRun(activeRun.run_id);
      setActiveRun(updated);
    } catch (err: any) {
      alert(`Failed to resume: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!activeRun) return;
    if (!window.confirm('Cancel active automation run?')) return;
    try {
      setIsLoading(true);
      const updated = await cancelRun(activeRun.run_id);
      setActiveRun(updated);
    } catch (err: any) {
      alert(`Failed to cancel: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitReviewDecision = async (
    reviewId: string,
    decision: 'APPROVED' | 'EDITED' | 'REJECTED' | 'UNAVAILABLE',
    editedValue?: any,
    note?: string
  ) => {
    if (!activeRun) return;
    try {
      const updated = await submitReviewDecision(
        activeRun.run_id,
        reviewId,
        decision,
        editedValue,
        note
      );
      setActiveRun(updated);
      setSelectedReviewModal(null);
      // Refresh pending reviews
      const reviews = await fetchPendingReviews(activeRun.run_id);
      setPendingReviews(reviews);
    } catch (err: any) {
      alert(`Review decision failed: ${err.message}`);
    }
  };

  const handleApproveSubmission = async (approved: boolean, notes?: string) => {
    if (!activeRun) return;
    try {
      setIsLoading(true);
      const updated = await approveSubmission(activeRun.run_id, approved, notes);
      setActiveRun(updated);
    } catch (err: any) {
      alert(`Submission approval failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="agent-dashboard-wrapper">
      <header className="agent-header">
        <div className="agent-header-brand">
          <span className="agent-header-icon">⚡</span>
          <div>
            <h1 className="agent-header-title">Insurance Portal AI Agent Control Center</h1>
            <p className="agent-header-subtitle">
              Closed-Loop Evidence Grounding &bull; Playwright Browser Automation &bull; Deterministic Safety Gates
            </p>
          </div>
        </div>
        <div className="agent-header-actions">
          <a
            href="/portal"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary btn-sm"
            data-testid="open-portal-external-link"
          >
            Open Portal Simulator ↗
          </a>
        </div>
      </header>

      <div className="agent-content-layout">
        {/* Left Column: Controls, Banner, Fields, Gates */}
        <div className="agent-main-column">
          <PatientSelector
            selectedPatientId={selectedPatientId}
            setSelectedPatientId={setSelectedPatientId}
            aiMode={aiMode}
            setAiMode={setAiMode}
            activeRun={activeRun}
            onStart={handleStart}
            onPause={handlePause}
            onResume={handleResume}
            onCancel={handleCancel}
            isLoading={isLoading}
          />

          <WorkflowStatusBanner run={activeRun} />

          {/* If final submission approval is required */}
          {activeRun?.state === 'SUBMISSION_APPROVAL_REQUIRED' && (
            <FinalSubmissionGate
              patientId={activeRun.patient_id}
              onApprove={handleApproveSubmission}
              isLoading={isLoading}
            />
          )}

          {/* If outcome is captured */}
          {activeRun?.outcome && (
            <OutcomeCard outcome={activeRun.outcome} patientId={activeRun.patient_id} />
          )}

          <DiscoveredFieldsTable
            fields={discoveredFields}
            proposedAnswers={proposedAnswers}
            pendingReviews={pendingReviews}
            onOpenReview={(r) => setSelectedReviewModal(r)}
          />
        </div>

        {/* Right Column: Audit Timeline */}
        <div className="agent-sidebar-column">
          <AuditTimeline events={auditEvents} />
        </div>
      </div>

      {/* Human Review Modal if open */}
      {selectedReviewModal && (
        <HumanReviewModal
          reviewItem={selectedReviewModal}
          onSubmitDecision={handleSubmitReviewDecision}
          onClose={() => setSelectedReviewModal(null)}
        />
      )}
    </div>
  );
};
