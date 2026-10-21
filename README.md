# Insurance Portal AI Agent (Prior Authorization Closed-Loop System)

A clinical prior-authorization automation system that integrates **Playwright browser automation**, **patient-scoped evidence retrieval**, **deterministic safety gating**, and a **human-in-the-loop review workflow** to complete dynamic payer portals safely and reliably.

---

## 1. What the Prototype Demonstrates

- **Closed-Loop Automation Flow**:
  `Observe` → `Understand` → `Retrieve` → `Propose` → `Validate` → `Fill` → `Verify` → `Re-observe`.
  The agent never scrapes once and blindly fills fields; it inspects the live DOM, computes page version fingerprints, and reacts to dynamic branching questions triggered by earlier answers.
- **Dynamic Branching & Clearing**:
  - Cancer type changes dynamically adapt biomarker question panels (Breast, Lung, Colorectal, Prostate, Lymphoma). Changing the parent disease clears dependent questions.
  - Selecting `metastatic = Yes` reveals metastasis sites, confirmation date, and evidence source.
  - Previous therapy branches dynamically display regimen history and toxicity detail textareas.
  - Required biomarker and recent laboratory rules enforce clinical compliance.
- **Strict Evidence Grounding & Zero Hallucination**:
  - The AI model only *proposes* structured answers with explicit evidence citations (`record_id`, `source_type`, `event_date`, `supporting_text`, `directness`).
  - Strict patient scoping ensures data from one patient is **never** used for another.
- **Deterministic Safety & Risk Gate**:
  - **Green (Auto-fill)**: Administrative demographic identifiers (Name, DOB, Sex, Address, Member ID, Provider NPI).
  - **Yellow (Fill with review flag)**: Direct clinical laboratory & pathology measurements.
  - **Orange (Human review required before proceeding)**: Disease stage inferences, prior systemic therapy, line of therapy.
  - **Red (Hard Stop / Pause)**: Identity mismatch, missing evidence, conflicting records, outdated laboratory results (> 30 days).
- **Human Review & Attestation Gate**:
  - Review modal allows clinicians to inspect exact portal questions, proposed values, supporting evidence, and conflicts.
  - Clinicians can **Approve**, **Edit & Approve**, **Reject**, or **Mark as Unavailable**. Edits are stored separately from the original AI proposal.
  - Final submission **always** requires explicit human attestation and approval.
- **Simulated Payer Portal Outcome**:
  - Payer portal evaluates submitted data and issues `VERIFIED`, `IN_INSPECTION`, or `CANCELLED` with confirmation number and timestamp.

---

## 2. What the Prototype Does Not Demonstrate

- Direct electronic data interchange (EDI 278) or FHIR DaVinci CRD/DTR/PAS transaction protocols.
- Bypassing 2FA, CAPTCHA, or bot-detection systems on third-party commercial portals without authorization.
- Automatic prescription alteration or autonomous clinical treatment decisions.

---

## 3. Architecture & Data Flow

```
[Agent Control Center] (React Dashboard /agent)
       │
       ▼  (REST / Server-Sent Events)
[FastAPI Backend Engine] ───► [LangGraph State Machine Engine]
       │                                │
       ├─► [Patient Data Service]       ├─► [Observation & Fingerprint Engine]
       │   (Strict Patient-ID Scoped)   ├─► [AI Reasoning: Mock / Real LLM]
       │                                ├─► [Deterministic Safety & Risk Gate]
       │                                └─► [Human Review / Escalation Queue]
       ▼
[Playwright Browser Automation] (Headed / Headless)
       │
       ▼
[Insurance Portal Simulator] (React Multi-Step Portal /portal)
```

### Responsibilities Matrix

| Responsibility | Handled By | Details |
| :--- | :--- | :--- |
| **Question Interpretation & Concept Mapping** | AI Provider (Mock / LLM) | Interprets question semantics, extracts normalized concepts, selects relevant patient retrieval tools. |
| **Evidence Retrieval & Patient Scoping** | `PatientService` | Controlled service requiring `patient_id`; returns verified clinical provenance. |
| **Value Verification & Recency Check** | `DeterministicValidator` | Enforces allowed values, 30-day lab recency, and conflict checks deterministically in Python. |
| **DOM Inspection & Field Filling** | Playwright Automation | Reads visible controls, fills verified answers, verifies DOM state after input. |
| **High-Risk Approval & Final Attestation** | Human Reviewer | Approves orange/red risk answers, edits discrepancies, and explicitly authorizes final submission. |
| **Final Prior Authorization Decision** | Payer Portal Simulator | Computes `VERIFIED`, `IN_INSPECTION`, or `CANCELLED` based on clinical criteria. |

---

## 4. Project Structure

```text
insurance-portal-ai-agent/
├── README.md
├── Makefile
├── .env.example
├── data/
│   └── patients.json               # 10 synthetic patient records with rich provenance
├── backend/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                 # FastAPI application entrypoint
│   │   ├── config.py               # Application settings
│   │   ├── database.py             # SQLAlchemy SQLite engine
│   │   ├── models/                 # AutomationRun, AuditEvent, HumanReview models
│   │   ├── schemas/                # Strict Pydantic contracts (AI, Portal, Patient, Run)
│   │   ├── patient_data/           # PatientService with strict patient scoping
│   │   ├── ai/                     # MockAIProvider and OpenAIAIProvider
│   │   ├── automation/             # Playwright browser manager, observer, and filler
│   │   ├── validation/             # Deterministic rules & risk classification
│   │   ├── workflow/               # LangGraph 22-state machine orchestration engine
│   │   ├── review/                 # Human review queue manager
│   │   ├── audit/                  # Audit trail logger & SSE broadcaster
│   │   └── api/                    # REST endpoints & SSE streams
│   └── tests/                      # Pytest unit, safety, and E2E scenario test suite
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── portal/                 # Insurance Portal Simulator (7 dynamic steps)
        ├── agent/                  # Agent Control Center (Timeline, Reviews, Stats)
        ├── components/             # Reusable UI components (StatCard, Badge, Header)
        └── api/                    # Backend API client
```

---

## 5. Synthetic Demo Patients & Scenarios

| Patient ID | Name | Clinical Domain | Scenario & Expected Outcome |
| :--- | :--- | :--- | :--- |
| **P1001** | Eleanor Vance | Breast Cancer (Stage IV) | **Complete Case**: Full evidence, HER2+, recent labs. Successfully verified to `VERIFIED`. |
| **P1002** | Marcus Chen | Lung Cancer (Adenocarcinoma) | **Dynamic Lung Panel**: Displays lung-specific biomarkers (EGFR+, ALK-, PD-L1 75%). |
| **P1003** | Sophia Rodriguez | Colorectal Cancer (Stage IV) | **Metastatic CRC**: Demonstrates liver/peritoneal metastases and KRAS wild-type targeted therapy. |
| **P1004** | David Kim | Male Breast Cancer (Recurrent) | **Prior Therapy & Toxicity**: Prior AC-T discontinued due to neurotoxicity; prior radiation and surgery. |
| **P1005** | Arthur Pendelton | Colorectal Cancer | **Missing Evidence**: Missing required KRAS/NRAS molecular test for Panitumumab. Pauses at `HUMAN_REVIEW_REQUIRED`. |
| **P1006** | Beatrice Miller | Breast Cancer | **Conflicting Evidence**: Discordant HER2 results (IHC 1- vs FISH amplified). Pauses for conflict arbitration. |
| **P1007** | Gregory House | Lung Cancer (Squamous) | **Outdated Lab Result**: Creatinine drawn 144 days ago (>30 days limit). Flags critical policy violation. |
| **P1008** | Claire Bennett | Breast Cancer | **Identity Mismatch**: Registration DOB (1985-04-12) conflicts with EMR (1975-04-12). Quarantined at `IDENTITY_REVIEW_REQUIRED`. |
| **P1009** | Robert Baratheon | Prostate Cancer (mCRPC) | **Castration Resistance**: Rising PSA (45.2), castrate testosterone, Enzalutamide therapy. |
| **P1010** | Diana Prince | Lymphoma (DLBCL) | **Lymphoma Panel**: CD20+, Ann Arbor Stage III, Bone marrow uninvolved, R-CHOP regimen. |

---

## 6. Setup & Execution Instructions

### Prerequisites
- Python 3.11+
- Node.js v18+ and npm
- Windows, macOS, or Linux

---

### Step 1: Install Dependencies

```bash
# 1. Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\activate   # On Windows (or source venv/bin/activate on Unix)

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Install Playwright Chromium browser
playwright install chromium

# 4. Install frontend dependencies
cd frontend
npm install
cd ..
```

---

### Step 2: Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default configuration for offline deterministic execution (zero API key needed):
```env
AI_MODE=mock
HEADLESS=false
PORTAL_BASE_URL=http://localhost:5173/portal
DATABASE_URL=sqlite:///./insurance_agent.db
```

For real OpenAI-compatible LLM mode:
```env
AI_MODE=llm
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o
```

---

### Step 3: Run the Servers

#### Terminal 1: Start Backend (FastAPI)
```bash
.\venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
API runs at: `http://127.0.0.1:8000` (Docs at `http://127.0.0.1:8000/docs`).

#### Terminal 2: Start Frontend (React + Vite)
```bash
cd frontend
npm run dev
```
Application runs at: `http://localhost:5173/`.

---

### Step 4: Run Automation

1. Open **Agent Control Center**: `http://localhost:5173/agent`.
2. Select any synthetic patient (e.g., click **P1001** for complete success, **P1006** for conflicting HER2, or **P1008** for identity mismatch).
3. Click **Start Automation**.
4. A Playwright browser window will open automatically, navigating to the portal at `http://localhost:5173/portal`.
5. Watch the agent inspect visible fields, retrieve patient evidence, fill verified values, and detect dynamic branching.
6. When paused (for human review or final submission), interact with the dashboard:
   - For **Review**: Click **Review Required** on the dashboard, inspect the evidence citations, and click **Approve** or **Edit & Approve**.
   - For **Final Submission**: Review the summary, check the clinical attestation, and click **Approve & Submit to Insurance Portal**.
7. The simulated outcome (`VERIFIED`, `IN_INSPECTION`, or `CANCELLED`) and confirmation number will display in real time.

---

### Step 5: Run Tests

Run the complete test suite (unit tests, validation rules, AI provider tests, safety gates, and Playwright end-to-end scenarios):

```bash
# Run all tests
.\venv\Scripts\pytest backend/tests -v

# Run unit & safety tests only
.\venv\Scripts\pytest backend/tests/test_patient_service.py backend/tests/test_validation.py backend/tests/test_ai_provider.py backend/tests/test_safety_security.py backend/tests/test_workflow.py -v

# Run Playwright E2E scenario tests only
.\venv\Scripts\pytest backend/tests/test_e2e_scenarios.py -v
```

---

## 7. Known Limitations & Production Path

### Why this is a prototype and not production-ready:
1. **Simulated Payer Portal**: Commercial payers (CoverMyMeds, Availity, Optum) use varying multi-factor authentication, session cookies, and dynamic anti-scraping protections.
2. **Synthetic Data**: Uses completely synthetic patient records in JSON format rather than a live FHIR or OncoEMR HL7 interface.
3. **Local Database**: Uses SQLite for local persistence rather than an enterprise HIPAA-compliant PostgreSQL cluster with field-level encryption.

### Path to Processing Real Protected Health Information (PHI):
1. **HIPAA Compliance**: Business Associate Agreements (BAAs) with all AI and cloud infrastructure providers. Zero-retention LLM endpoints to ensure PHI is not logged or used for model training.
2. **Audit & Access Control**: Role-Based Access Control (RBAC), SSO via SAML/OAuth2, and tamper-evident cryptographic audit logging.
3. **EHR Integration**: Direct FHIR US-Core and DaVinci CRD/DTR integrations to retrieve live clinical notes and pathology reports.
4. **Payer Adapter Architecture**: Replace the simulated portal browser automation with approved EDI 278 / FHIR PAS clearinghouse APIs wherever available, utilizing browser automation only for fallback web-only portals.

---

## 8. Summary of Commands

```text
# Install
python -m venv venv && .\venv\Scripts\pip install -r backend\requirements.txt && .\venv\Scripts\playwright install chromium && cd frontend && npm install && cd ..

# Start backend
.\venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload

# Start frontend
cd frontend && npm run dev

# Run unit tests
.\venv\Scripts\pytest backend/tests/test_validation.py backend/tests/test_patient_service.py -v

# Run end-to-end tests
.\venv\Scripts\pytest backend/tests/test_e2e_scenarios.py -v
```
