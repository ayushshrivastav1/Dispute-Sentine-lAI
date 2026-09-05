# DisputeSentinel AI

> **Evidence-backed, explainable dispute automation for Razorpay merchants**

DisputeSentinel AI is an agentic dispute-response system designed to reduce the manual effort involved in investigating payment disputes.

Instead of asking an LLM to make an unrestricted financial decision, DisputeSentinel separates **AI-powered evidence understanding** from a **deterministic policy gate**. The agent gathers and structures evidence, while bounded rules decide whether a dispute is eligible for automatic contesting or must be escalated to a human.

---

## Why DisputeSentinel?

A payment dispute can require a merchant to investigate information across several systems:

- Payment/dispute details
- Delivery and carrier information
- Proof of delivery
- Signature/recipient evidence
- Customer/order context
- Device/IP risk signals
- Supporting documents

Manual investigation is slow and difficult to scale.

DisputeSentinel turns this into an auditable workflow:

```text
Razorpay Dispute
       |
       v
Webhook Verification
       |
       v
Evidence Collection
       |
       +---- Carrier Verification
       |
       +---- Vision / OCR
       |
       v
Structured Evidence
       |
       v
LLM Evidence / Contest Dossier
       |
       v
Deterministic Policy Gate
       |
       +----------------------+
       |                      |
       v                      v
AUTO CONTEST            HUMAN REVIEW
       |
       v
Razorpay Contest API
       |
       v
Audit Ledger
```

---

## Core Design Principle

### AI analyzes. Policy controls financial action.

The LLM is used for tasks such as:

- Understanding unstructured evidence
- Extracting useful information
- Generating structured dispute dossiers
- Summarizing supporting evidence

The LLM does **not** get unrestricted authority to execute financial actions.

Automatic contesting is bounded by deterministic controls including:

- Evidence requirements
- Confidence thresholds
- Win-probability threshold
- Maximum auto-contest amount
- Risk signals
- Human escalation for uncertain cases

This creates a separation between **probabilistic AI reasoning** and **deterministic financial controls**.

---

# Features

## 1. Agentic dispute workflow

Built with LangGraph, the system orchestrates a stateful dispute-processing workflow.

The workflow can:

1. Receive a dispute
2. Collect evidence
3. Verify carrier information
4. Analyze proof-of-delivery material
5. Generate an evidence-backed contest dossier
6. Evaluate the case through a policy gate
7. Contest eligible disputes
8. Escalate uncertain cases
9. Record an audit trail

---

## 2. Razorpay integration

DisputeSentinel includes a Razorpay API client for dispute operations.

Supported operations include:

```text
GET   /v1/disputes/{id}
PATCH /v1/disputes/{id}/contest
POST  /v1/disputes/{id}/accept
POST  /v1/documents
```

The application also supports Razorpay webhook signature verification.

### Safety defaults

Financial actions are disabled by default:

```env
RAZORPAY_LIVE_ACTIONS=false
RAZORPAY_UPLOAD_EVIDENCE=false
```

Enable live actions only in an explicitly controlled environment.

---

## 3. Webhook security and idempotency

Incoming Razorpay webhooks are verified using the Razorpay webhook signature.

The system also uses the Razorpay event ID to prevent duplicate webhook processing.

Conceptually:

```text
Webhook
   |
   +--> Signature verification
   |
   +--> Event ID check
           |
           +--> Already processed -> ignore safely
           |
           +--> New event -> process
```

This is important because webhook delivery can be retried.

---

## 4. Multi-provider AI

The system supports configurable LLM providers.

Current configuration supports:

```env
LLM_PROVIDER=groq
```

with Groq's Llama models, while OpenAI can be configured for vision/OCR workloads.

The vision pipeline is designed to degrade safely when an external model is unavailable rather than allowing an AI outage to become an uncontrolled financial action.

---

## 5. Deterministic policy gate

The policy engine is intentionally separated from the LLM.

A simplified decision flow is:

```text
Evidence
   |
   v
Win Probability
   |
   +--> Strong evidence
   |       +
   |     Amount below auto-contest limit
   |       +
   |     Required evidence present
   |       |
   |       v
   |   AUTO_CONTEST
   |
   +--> Otherwise
           |
           v
      HUMAN_REVIEW
```

Default configuration:

```env
AUTO_CONTEST_THRESHOLD=0.75
AUTO_ACCEPT_THRESHOLD=0.40
MAX_AUTO_CONTEST_AMOUNT=2500000
```

`MAX_AUTO_CONTEST_AMOUNT=2500000` represents ₹25,000 when the API amount is expressed in paise.

---

## 6. Human escalation

Not every dispute should be automated.

DisputeSentinel can escalate cases when:

- Evidence is insufficient
- Evidence confidence is low
- Signals conflict
- The dispute exceeds the configured automatic-action limit
- The policy score is below the required threshold
- An external dependency fails

The objective is not maximum automation.

The objective is **safe automation of high-confidence cases**.

---

## 7. Evidence-backed audit trail

Each decision records context such as:

```text
Dispute ID
Decision
Policy score
Policy threshold
Evidence used
Policy version
Action
Success/failure
Timestamp
```

This allows a reviewer to answer:

> What did the system do?

and:

> Why did it do it?

---

# Evaluation

DisputeSentinel includes a reproducible evaluation pipeline using a **synthetic held-out test dataset**.

Dataset:

```text
dataset/
├── development.csv
├── disputes.csv
└── held_out_test.csv
```

The evaluation script executes the evaluation adapter and reports:

- Precision
- Recall
- F1
- Accuracy
- False-positive rate
- Confusion matrix
- Recovered disputed capital
- False-positive cost
- Net value saved
- ROI multiplier

Run:

```bash
PYTHONPATH=. python evaluation/evaluate.py
```

Or run the benchmark test:

```bash
PYTHONPATH=. pytest -q tests/test_evaluation_benchmark.py
```

### Current benchmark

The repository contains a 60-case synthetic held-out evaluation benchmark.

Reported results:

| Metric | Result |
|---|---:|
| Evaluation cases | 60 |
| Precision | 97.73% |
| Recall | 100.00% |
| F1 | 98.85% |
| Accuracy | 98.33% |
| False Positive Rate | 5.88% |
| True Positives | 43 |
| False Positives | 1 |
| True Negatives | 16 |
| False Negatives | 0 |

### Financial impact model

The benchmark also estimates the cost of false positives.

For the current synthetic benchmark:

```text
Total disputed capital:      ₹21.07 lakh
Recovered capital (TP):      ₹18.83 lakh
False-positive cost:         ₹1,500
Net value saved:             ₹18.82 lakh
```

These are **synthetic evaluation results**, not production Razorpay merchant results.

The benchmark is intended to demonstrate the evaluation methodology and the behavior of the deterministic risk policy.

---

# Architecture

```text
                         +----------------------+
                         |       Razorpay       |
                         +----------+-----------+
                                    |
                              Dispute Webhook
                                    |
                                    v
                         +----------------------+
                         | Webhook Verification |
                         | + Idempotency        |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |     LangGraph        |
                         |   Agent Workflow     |
                         +----------+-----------+
                                    |
                +-------------------+-------------------+
                |                   |                   |
                v                   v                   v
        +---------------+   +---------------+   +---------------+
        | Carrier APIs  |   | Vision / OCR  |   | Order / DB    |
        +---------------+   +---------------+   +---------------+
                |                   |                   |
                +-------------------+-------------------+
                                    |
                                    v
                         +----------------------+
                         | Structured Evidence  |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | LLM / Groq / OpenAI  |
                         | Evidence Dossier     |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Deterministic Policy |
                         |       Gate           |
                         +----------+-----------+
                                    |
                         +----------+----------+
                         |                     |
                         v                     v
                  +-------------+       +-------------+
                  | Auto Contest|       | Human Review|
                  +------+------+       +-------------+
                         |
                         v
                  +-------------+
                  | Razorpay API|
                  +------+------+
                         |
                         v
                  +-------------+
                  | Audit Ledger|
                  +-------------+
```

---

# Project Structure

```text
Dispute-Sentine-lAI-main/
│
├── agent/
│   ├── graph/
│   │   ├── executor.py
│   │   └── state.py
│   │
│   ├── nodes/
│   │   ├── escalation.py
│   │   ├── extractor.py
│   │   ├── generator.py
│   │   ├── policy_gate.py
│   │   └── vision_ocr.py
│   │
│   ├── prompts/
│   ├── schemas/
│   └── tools/
│       ├── carrier_api.py
│       ├── db_client.py
│       ├── razorpay_sdk.py
│       └── registry.py
│
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       │       ├── analytics.py
│       │       ├── auth.py
│       │       ├── disputes.py
│       │       ├── health.py
│       │       ├── review_queue.py
│       │       └── webhooks.py
│       │
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       └── main.py
│
├── dataset/
│   ├── development.csv
│   ├── disputes.csv
│   └── held_out_test.csv
│
├── evaluation/
│   ├── evaluate.py
│   ├── pipeline_adapter.py
│   └── benchmark_report.json
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── README.md
│
├── tests/
│   └── test_evaluation_benchmark.py
│
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

# Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite for local development
- PostgreSQL for production/container deployment
- Pydantic
- HTTPX

### AI / Agent

- LangGraph
- LangChain
- Groq
- OpenAI
- Multimodal vision/OCR pipeline

### Frontend

- React
- TypeScript
- Vite
- React Router
- TanStack React Query
- Recharts
- Tailwind CSS
- Radix UI

### Security

- Razorpay webhook signature verification
- JWT authentication
- Password hashing
- Environment-based secrets
- Bounded financial actions
- Audit logging
- Duplicate webhook protection

### Testing / Evaluation

- Pytest
- Pandas
- Scikit-learn
- Synthetic evaluation dataset

---

# Local Setup

## 1. Clone

```bash
git clone <YOUR_PUBLIC_GITHUB_REPOSITORY_URL>
cd Dispute-Sentine-lAI-main
```

## 2. Create Python environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment

Copy:

```text
.env.example
```

to:

```text
.env
```

Then configure the required values.

Minimum AI configuration:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key
```

For Razorpay integration:

```env
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
```

For local development, SQLite can be used:

```env
DATABASE_URL=sqlite+aiosqlite:///./dispute_sentinel.db
```

For controlled demonstrations, keep:

```env
RAZORPAY_LIVE_ACTIONS=false
RAZORPAY_UPLOAD_EVIDENCE=false
```

Never commit `.env`.

---

# Run the Backend

From the repository root:

```bash
PYTHONPATH=. uvicorn backend.app.main:app --reload --port 8000
```

API:

```text
http://localhost:8000
```

Health endpoint:

```text
http://localhost:8000/api/v1/health
```

---

# Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend development server runs on the Vite development port.

Configure the backend URL through:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

# Docker

The repository includes Docker Compose configuration for:

- PostgreSQL
- FastAPI backend
- Vite frontend

Start the stack with:

```bash
docker compose up --build
```

Stop it with:

```bash
docker compose down
```

To remove the persisted PostgreSQL volume:

```bash
docker compose down -v
```

---

# Running the Evaluation

Run the complete held-out benchmark:

```bash
PYTHONPATH=. python evaluation/evaluate.py
```

Run the benchmark test:

```bash
PYTHONPATH=. pytest -q tests/test_evaluation_benchmark.py
```

The evaluation requires at least 50 cases in the held-out dataset.

The benchmark uses the repository's:

```text
dataset/held_out_test.csv
```

and is explicitly labeled as synthetic evaluation data.

---

# Safety Model

DisputeSentinel is designed around a defense-in-depth model.

### Layer 1 — Authentication

Protected backend operations require authenticated access.

### Layer 2 — Webhook verification

Incoming Razorpay webhook requests are cryptographically verified.

### Layer 3 — Evidence validation

Evidence is structured and checked before it reaches the policy gate.

### Layer 4 — Deterministic policy

The final automatic-action decision is controlled by deterministic rules rather than an unrestricted LLM response.

### Layer 5 — Monetary boundary

Automatic contesting is limited by the configured maximum dispute amount.

### Layer 6 — Human escalation

Low-confidence or unsupported cases are routed for human review.

### Layer 7 — Auditability

Decision context and action status are recorded.

---

# Failure Handling

The system is designed to degrade safely.

Examples:

```text
Groq unavailable
      |
      v
Configured fallback
      |
      v
Continue without unsafe financial automation
```

```text
Carrier API unavailable
      |
      v
Capture failure
      |
      v
Insufficient evidence
      |
      v
Human Review
```

```text
Duplicate Razorpay webhook
      |
      v
Event ID already processed
      |
      v
Do not process twice
```

The core safety principle is:

> **An external dependency failure must not automatically become a financial action.**

---

# API Overview

Representative endpoints include:

```text
GET  /api/v1/health

POST /api/v1/auth/login
POST /api/v1/auth/signup

GET  /api/v1/disputes
GET  /api/v1/disputes/{id}

POST /api/v1/disputes/{id}/contest
POST /api/v1/disputes/{id}/accept-loss

GET  /api/v1/review-queue

GET  /api/v1/analytics

POST /api/v1/webhooks/razorpay
```

Exact request/response models are defined in the backend schemas and route implementations.

---

# Security Notes

**Do not commit secrets.**

Never put these into Git:

```text
GROQ_API_KEY
OPENAI_API_KEY
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET
JWT_SECRET_KEY
DATABASE_PASSWORD
```

Use environment variables and keep `.env` ignored by Git.

For a hackathon/demo environment, keep live financial actions disabled unless they are explicitly required and controlled.

---

# Product Impact

DisputeSentinel targets four operational outcomes:

### 1. Faster dispute response

Automates evidence gathering and dossier preparation.

### 2. Reduced manual workload

Moves repetitive evidence investigation from manual operations into an agentic workflow.

### 3. Better consistency

Uses deterministic policy rules for automatic-action eligibility.

### 4. Explainable automation

Each decision can be traced back to evidence, policy thresholds and action status.

The system is intentionally designed around **safe automation rather than maximum automation**.

---

# Current Limitations

This project is a prototype / hackathon implementation and should not be interpreted as a production financial decision system.

Known limitations include:

- Evaluation data is synthetic.
- Carrier integrations depend on provider availability and credentials.
- Some environments use demo/fallback data.
- External model availability can affect AI inference.
- Production deployment requires additional operational controls, monitoring, compliance review and security hardening.
- Real Razorpay financial actions are disabled by default.

---

# Roadmap

Potential future improvements:

- Larger independently generated evaluation datasets
- More merchant/order integrations
- Additional carrier providers
- Human-review feedback loop
- Policy calibration based on production outcomes
- More sophisticated evidence provenance
- Production-grade observability
- Model/version performance tracking
- Cost-aware model routing
- Merchant-specific policy configuration

---

# Demo Flow

A recommended demonstration flow is:

```text
1. Incoming Razorpay dispute
2. Webhook verification
3. Evidence collection
4. Carrier verification
5. Vision / OCR analysis
6. AI evidence dossier
7. Deterministic policy score
8. AUTO_CONTEST for strong evidence
9. HUMAN_REVIEW for weak evidence
10. Audit record
11. Evaluation metrics
```

The most important product principle to demonstrate is:

> **AI understands the evidence; deterministic controls decide whether automation is allowed.**

---

# Why this approach?

Financial automation needs more than an LLM response.

A model can be useful for understanding documents and unstructured evidence, but a financial action should be:

- bounded
- explainable
- auditable
- testable
- reversible where possible
- subject to explicit policy

DisputeSentinel therefore treats the LLM as an **evidence and reasoning component**, not an unrestricted financial authority.

---

# Author

**Ayush Shrivastav**

Built as an AI/agentic fintech project for the Razorpay AI Buildathon.

---

## Disclaimer

This project is a prototype created for evaluation and demonstration purposes.

All benchmark data and reported financial-impact figures in this repository are synthetic and should not be interpreted as Razorpay production metrics, merchant performance, or guaranteed financial outcomes.

Razorpay and related product/API names are referenced for integration and demonstration purposes.
