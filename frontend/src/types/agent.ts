import { PortalSubmissionOutcome } from './portal';

export type WorkflowState =
  | 'CASE_CREATED'
  | 'IDENTITY_VALIDATION'
  | 'IDENTITY_REVIEW_REQUIRED'
  | 'PATIENT_DATA_LOADED'
  | 'PORTAL_SESSION_STARTING'
  | 'PORTAL_SESSION_READY'
  | 'PAGE_OBSERVING'
  | 'FIELDS_DISCOVERED'
  | 'EVIDENCE_RETRIEVING'
  | 'ANSWER_PROPOSING'
  | 'ANSWER_VALIDATING'
  | 'HUMAN_REVIEW_REQUIRED'
  | 'FIELD_FILLING'
  | 'FIELD_VERIFYING'
  | 'PAGE_RESCANNING'
  | 'PAGE_REVIEW_REQUIRED'
  | 'PAGE_COMPLETED'
  | 'SUBMISSION_APPROVAL_REQUIRED'
  | 'SUBMITTING'
  | 'OUTCOME_CAPTURED'
  | 'FAILED'
  | 'CANCELLED';

export type RiskLevel = 'green' | 'yellow' | 'orange' | 'red';

export type DecisionType =
  | 'PROPOSED'
  | 'INSUFFICIENT_EVIDENCE'
  | 'CONFLICT_REQUIRES_REVIEW'
  | 'IDENTITY_MISMATCH'
  | 'UNSUPPORTED_QUESTION'
  | 'INVALID_ALLOWED_VALUE';

export interface FieldEvidenceCitation {
  record_id: string;
  source_type: string;
  event_date?: string;
  supporting_text: string;
  directness: 'direct' | 'inferred' | 'historical';
}

export interface DiscoveredField {
  field_id: string;
  page_id: string;
  question_text: string;
  help_text?: string | null;
  input_type: 'text' | 'number' | 'date' | 'textarea' | 'select' | 'radio' | 'checkbox' | 'multi-select';
  allowed_values?: string[];
  required: boolean;
  visible: boolean;
  current_value?: any;
  depends_on?: string[];
  risk_category: 'administrative' | 'clinical' | 'sensitive' | 'high-risk';
  page_version: string;
}

export interface ProposedAnswer {
  patient_id: string;
  page_id: string;
  field_id: string;
  question_text: string;
  normalized_concept: string;
  answer_type: string;
  proposed_value: any;
  allowed_value_match: boolean;
  evidence: FieldEvidenceCitation[];
  conflicts: string[];
  missing_information: string[];
  validation_requirements: string[];
  risk_level: RiskLevel;
  decision: DecisionType;
  reason: string;
}

export interface HumanReviewItem {
  review_id: string;
  run_id: string;
  patient_id: string;
  page_id: string;
  field_id: string;
  question_text: string;
  proposed_value: any;
  input_type: string;
  allowed_values?: string[];
  evidence: FieldEvidenceCitation[];
  conflicts: string[];
  missing_information: string[];
  risk_level: RiskLevel;
  reason_for_escalation: string;
  status: 'PENDING' | 'APPROVED' | 'EDITED' | 'REJECTED' | 'UNAVAILABLE';
  human_decision?: string;
  human_edit_value?: any;
  reviewer_note?: string;
  screenshot_url?: string;
  created_at: string;
  resolved_at?: string;
}

export interface AuditEvent {
  event_id: string;
  run_id: string;
  patient_id: string;
  timestamp: string;
  transition?: string;
  portal_page?: string;
  field_id?: string;
  question_text?: string;
  page_version?: string;
  retrieved_evidence_ids?: string[];
  proposed_answer?: any;
  model_provider?: string;
  validation_results?: any;
  filled_value?: any;
  human_decision?: string;
  human_edit?: any;
  risk_level?: RiskLevel;
  error?: string;
  details?: Record<string, any>;
}

export interface AutomationRun {
  run_id: string;
  patient_id: string;
  state: WorkflowState;
  current_page: string;
  created_at: string;
  updated_at: string;
  is_paused: boolean;
  fields_discovered_count: number;
  fields_filled_count: number;
  pending_reviews_count: number;
  conflicts_count: number;
  ai_mode: 'mock' | 'llm';
  model_name?: string;
  outcome?: PortalSubmissionOutcome;
  error_message?: string;
}
