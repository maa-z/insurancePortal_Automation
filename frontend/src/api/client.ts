import { AutomationRun, HumanReviewItem, AuditEvent } from '../types/agent';
import { SyntheticPatient } from '../types/patient';

const API_BASE = '/api';

export async function fetchPatients(): Promise<SyntheticPatient[]> {
  const res = await fetch(`${API_BASE}/patients`);
  if (!res.ok) throw new Error('Failed to load patient records');
  return res.json();
}

export async function fetchPatient(patientId: string): Promise<SyntheticPatient> {
  const res = await fetch(`${API_BASE}/patients/${patientId}`);
  if (!res.ok) throw new Error(`Patient ${patientId} not found`);
  return res.json();
}

export async function startAutomationRun(patientId: string, aiMode: 'mock' | 'llm' = 'mock'): Promise<AutomationRun> {
  const res = await fetch(`${API_BASE}/automation/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ patient_id: patientId, ai_mode: aiMode }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to start automation run');
  }
  return res.json();
}

export async function fetchRun(runId: string): Promise<AutomationRun> {
  const res = await fetch(`${API_BASE}/automation/runs/${runId}`);
  if (!res.ok) throw new Error(`Run ${runId} not found`);
  return res.json();
}

export async function pauseRun(runId: string): Promise<AutomationRun> {
  const res = await fetch(`${API_BASE}/automation/runs/${runId}/pause`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to pause run');
  return res.json();
}

export async function resumeRun(runId: string): Promise<AutomationRun> {
  const res = await fetch(`${API_BASE}/automation/runs/${runId}/resume`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to resume run');
  return res.json();
}

export async function cancelRun(runId: string): Promise<AutomationRun> {
  const res = await fetch(`${API_BASE}/automation/runs/${runId}/cancel`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to cancel run');
  return res.json();
}

export async function fetchPendingReviews(runId: string): Promise<HumanReviewItem[]> {
  const res = await fetch(`${API_BASE}/automation/runs/${runId}/reviews`);
  if (!res.ok) return [];
  return res.json();
}

export async function submitReviewDecision(
  runId: string,
  reviewId: string,
  decision: 'APPROVED' | 'EDITED' | 'REJECTED' | 'UNAVAILABLE',
  editedValue?: any,
  reviewerNote?: string
): Promise<AutomationRun> {
  const res = await fetch(`${API_BASE}/automation/runs/${runId}/reviews/${reviewId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      decision,
      edited_value: editedValue,
      reviewer_note: reviewerNote,
    }),
  });
  if (!res.ok) throw new Error('Failed to submit review decision');
  return res.json();
}

export async function approveSubmission(runId: string, approved: boolean, notes?: string): Promise<AutomationRun> {
  const res = await fetch(`${API_BASE}/automation/runs/${runId}/submission-approval`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved, notes }),
  });
  if (!res.ok) throw new Error('Failed to submit final submission decision');
  return res.json();
}

export async function fetchAuditTimeline(runId: string): Promise<AuditEvent[]> {
  const res = await fetch(`${API_BASE}/automation/runs/${runId}/audit`);
  if (!res.ok) return [];
  return res.json();
}
