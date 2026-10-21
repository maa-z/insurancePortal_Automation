import React from 'react';
import { AutomationRun } from '../types/agent';

interface PatientSelectorProps {
  selectedPatientId: string;
  setSelectedPatientId: (id: string) => void;
  aiMode: 'mock' | 'llm';
  setAiMode: (mode: 'mock' | 'llm') => void;
  activeRun: AutomationRun | null;
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onCancel: () => void;
  isLoading: boolean;
}

const PRESET_PATIENTS = [
  { id: 'P1001', name: 'Eleanor Vance', tag: 'Complete / Verified', desc: 'Breast Stage IV, HER2+, Full evidence' },
  { id: 'P1002', name: 'Marcus Chen', tag: 'Dynamic Lung Panel', desc: 'Lung Adeno, EGFR+, PD-L1 75%' },
  { id: 'P1003', name: 'Sophia Rodriguez', tag: 'Metastatic CRC', desc: 'Colorectal, Liver/Peritoneum, KRAS WT' },
  { id: 'P1004', name: 'David Kim', tag: 'Prior Tx Toxicity', desc: 'Male Breast, Prior AC-T ended for neuropathy' },
  { id: 'P1005', name: 'Arthur Pendelton', tag: 'Missing Evidence', desc: 'CRC, Missing KRAS/NRAS for Panitumumab' },
  { id: 'P1006', name: 'Beatrice Miller', tag: 'Conflicting HER2', desc: 'Discordant HER2 (IHC 1- vs FISH +)' },
  { id: 'P1007', name: 'Gregory House', tag: 'Outdated Lab', desc: 'Creatinine from 144 days ago (>30d limit)' },
  { id: 'P1008', name: 'Claire Bennett', tag: 'Identity Mismatch', desc: 'DOB discrepancy registration vs EMR' },
  { id: 'P1009', name: 'Robert Baratheon', tag: 'Prostate mCRPC', desc: 'Castration resistant, PSA 45.2, Enzalutamide' },
  { id: 'P1010', name: 'Diana Prince', tag: 'Lymphoma Stage III', desc: 'DLBCL CD20+, R-CHOP regimen' },
];

export const PatientSelector: React.FC<PatientSelectorProps> = ({
  selectedPatientId,
  setSelectedPatientId,
  aiMode,
  setAiMode,
  activeRun,
  onStart,
  onPause,
  onResume,
  onCancel,
  isLoading,
}) => {
  const isRunning = Boolean(
    activeRun &&
    !['OUTCOME_CAPTURED', 'FAILED', 'CANCELLED'].includes(activeRun.state)
  );

  const isPaused = Boolean(
    activeRun?.state === 'HUMAN_REVIEW_REQUIRED' ||
    activeRun?.state === 'PAGE_REVIEW_REQUIRED' ||
    activeRun?.state === 'SUBMISSION_APPROVAL_REQUIRED' ||
    activeRun?.is_paused
  );

  return (
    <div className="agent-card patient-selector-card">
      <div className="card-header">
        <h3 className="card-title">Case Initiation & Patient Target</h3>
        <div className="ai-mode-pill-toggle">
          <button
            type="button"
            className={`mode-toggle-btn ${aiMode === 'mock' ? 'active' : ''}`}
            onClick={() => setAiMode('mock')}
            disabled={isRunning}
            data-testid="ai-mode-mock-btn"
          >
            Deterministic Mock AI
          </button>
          <button
            type="button"
            className={`mode-toggle-btn ${aiMode === 'llm' ? 'active' : ''}`}
            onClick={() => setAiMode('llm')}
            disabled={isRunning}
            data-testid="ai-mode-llm-btn"
          >
            Real LLM Mode
          </button>
        </div>
      </div>

      <div className="preset-patient-grid" data-testid="preset-patient-selector">
        {PRESET_PATIENTS.map((p) => {
          const isSelected = selectedPatientId === p.id;
          return (
            <button
              key={p.id}
              type="button"
              className={`patient-preset-chip ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedPatientId(p.id)}
              disabled={isRunning}
              data-testid={`preset-patient-${p.id}`}
            >
              <div className="chip-header">
                <span className="chip-id mono">{p.id}</span>
                <span className="chip-badge">{p.tag}</span>
              </div>
              <div className="chip-name">{p.name}</div>
              <div className="chip-desc">{p.desc}</div>
            </button>
          );
        })}
      </div>

      <div className="custom-patient-row">
        <div className="input-group">
          <label htmlFor="agent-patient-id-input" className="form-label">
            Target Patient Identifier
          </label>
          <input
            id="agent-patient-id-input"
            data-testid="agent-patient-id-input"
            type="text"
            className="form-input mono"
            placeholder="e.g. P1001"
            value={selectedPatientId}
            onChange={(e) => setSelectedPatientId(e.target.value)}
            disabled={isRunning}
          />
        </div>

        <div className="action-buttons-group">
          {!isRunning ? (
            <button
              type="button"
              className="btn btn-primary btn-large"
              id="start-automation-btn"
              data-testid="start-automation-button"
              onClick={onStart}
              disabled={!selectedPatientId || isLoading}
            >
              {isLoading ? 'Starting Run...' : 'Start Automation'}
            </button>
          ) : (
            <>
              {isPaused ? (
                <button
                  type="button"
                  className="btn btn-success"
                  id="resume-automation-btn"
                  data-testid="resume-automation-button"
                  onClick={onResume}
                  disabled={isLoading}
                >
                  Resume Automation
                </button>
              ) : (
                <button
                  type="button"
                  className="btn btn-warning"
                  id="pause-automation-btn"
                  data-testid="pause-automation-button"
                  onClick={onPause}
                  disabled={isLoading}
                >
                  Pause
                </button>
              )}
              <button
                type="button"
                className="btn btn-danger"
                id="cancel-automation-btn"
                data-testid="cancel-automation-button"
                onClick={onCancel}
                disabled={isLoading}
              >
                Cancel Run
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
