## Twin AI (AI Digital Twin)

Full-stack “digital twin” chat app:

- **Frontend**: Next.js (App Router) + React + Tailwind — a clean chat UI that talks to an API and keeps a `session_id`.
- **Backend**: FastAPI API that calls **AWS Bedrock** (Converse API) and stores conversation memory **locally (JSON)** or in **S3**.
- **Cloud deployment**: Serverless backend on **AWS Lambda + API Gateway**, static frontend on **S3 + CloudFront**, provisioned with **Terraform** and automated via **GitHub Actions**.

---

## Features

- **Digital twin chat** backed by AWS Bedrock (`POST /chat`)
- **Session memory** persisted per `session_id` (S3 in cloud, JSON files locally)
- **Conversation retrieval** (`GET /conversation/{session_id}`)
- **Infra as Code**: Lambda, API Gateway, S3 (frontend + memory), CloudFront (+ optional custom domain)
- **One-command deployment** scripts for macOS/Linux (`scripts/deploy.sh`) and Windows (`scripts/deploy.ps1`)

---

## Architecture (high level)

```mermaid
flowchart LR
  U[User Browser] --> CF[CloudFront]
  CF --> S3FE[S3 (static frontend)]
  U -->|/chat| APIGW[API Gateway HTTP API]
  APIGW --> L[Lambda (FastAPI via Mangum)]
  L --> BR[AWS Bedrock Runtime]
  L --> S3MEM[S3 (conversation memory)]
```

---

## Repo structure

- `frontend/`: Next.js UI (static export)
- `backend/`: FastAPI API + Lambda adapter (`mangum`)
- `terraform/`: AWS infrastructure
- `scripts/`: deploy/destroy helpers (bash + PowerShell)
- `memory/`: local conversation history (ignored by git)

---

## Local development

### Prerequisites

- Node.js **20+**
- Python **3.12+**
- AWS credentials available locally (for Bedrock calls), e.g. via `aws configure`

### 1) Backend (FastAPI)

From the repo root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Backend defaults:

- **API**: `http://localhost:8000`
- **CORS**: allows `http://localhost:3000` by default
- **Memory**: local JSON files under `../memory/`

### 2) Frontend (Next.js)

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The frontend will call:

- `NEXT_PUBLIC_API_URL` if set, otherwise `http://localhost:8000`

---

## Configuration

### Backend environment variables

The backend reads from environment variables (and `.env` if present).

- **`DEFAULT_AWS_REGION`**: AWS region for Bedrock (default `us-east-1`)
- **`BEDROCK_MODEL_ID`**: Bedrock model id (default `global.amazon.nova-2-lite-v1:0`)
- **`CORS_ORIGINS`**: comma-separated origins (default `http://localhost:3000`)
- **`USE_S3`**: `true` to store memory in S3 (default `false`)
- **`S3_BUCKET`**: bucket name for memory when `USE_S3=true`
- **`MEMORY_DIR`**: local memory directory (default `../memory`)

### Frontend environment variables

- **`NEXT_PUBLIC_API_URL`**: API base URL (local: `http://localhost:8000`, cloud: API Gateway URL)

---

## Customizing the “twin” data

The system prompt is built in `backend/context.py` using data loaded from `backend/data/` via `backend/resoruces.py`.

You can replace/add your own files:

- `backend/data/facts.json`
- `backend/data/me.txt` (or `summary.txt` if you add it)
- `backend/data/style.txt`
- `backend/data/linkedin.pdf` (optional)

Note: avoid committing sensitive personal data to a public repo.

---

## Deploy to AWS (Terraform)

This repo deploys:

- Frontend: **S3 static website** + **CloudFront**
- Backend: **Lambda (Python 3.12)** + **API Gateway HTTP API**
- Memory: **S3 bucket**

### 1) One-time: Terraform remote state (recommended)

The deploy/destroy scripts expect:

- S3 bucket: `twin-terraform-state-<aws_account_id>`
- DynamoDB table: `twin-terraform-locks`

There’s a walkthrough in `week2/day5.md` (see “Set Up S3 Backend for Terraform State”).

### 2) Deploy (Windows / PowerShell)

```powershell
.\scripts\deploy.ps1 -Environment dev -ProjectName twin
```

### 3) Deploy (macOS/Linux)

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh dev twin
```

The deploy script will:

- build `backend/lambda-deployment.zip`
- apply Terraform in the selected workspace (`dev`, `test`, `prod`)
- build the Next.js static export and sync it to the S3 frontend bucket

### 4) Destroy

PowerShell:

```powershell
.\scripts\destroy.ps1 -Environment dev -ProjectName twin
```

Bash:

```bash
chmod +x scripts/destroy.sh
./scripts/destroy.sh dev twin
```

---

## CI/CD (GitHub Actions)

- `Deploy Digital Twin`: deploys on pushes to `main` (or manual dispatch) using OIDC + an AWS role.
- `Destroy Environment`: manual dispatch with a confirmation prompt.

You’ll need to configure repository secrets like `AWS_ROLE_ARN`, `AWS_ACCOUNT_ID`, and `DEFAULT_AWS_REGION`.

