# SafeMail by Strikepoint Security

AI-assisted phishing email analysis tool. Upload `.eml` files to detect phishing indicators, verify email authentication, and get an AI-powered verdict.

## Features

- **EML File Analysis** — Drag-and-drop upload with full email parsing
- **10 Security Checks** — SPF, DKIM, DMARC, From/Reply-To mismatch, display name spoofing, embedded URL analysis, attachment risk, header path analysis, subject line analysis
- **AI Analyst Verdict** — Claude AI synthesizes all findings into a confidence-rated verdict
- **Risk Score** — 0-100 composite score with visual gauge
- **Session History** — View previously analyzed emails in your session

## Tech Stack

- **Backend**: Python, FastAPI, Anthropic SDK
- **Frontend**: React, Vite, Tailwind CSS, React Router
- **AI**: Claude (via Anthropic API)

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env if your backend is not at http://localhost:8000
npm run dev
```

The app will be available at `http://localhost:5173`.

## Environment Variables

### Backend

| Variable | Description | Required |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude AI verdicts | Yes |
| `FRONTEND_URL` | Frontend origin for CORS (default: `http://localhost:5173`) | No |

### Frontend

| Variable | Description | Required |
|---|---|---|
| `VITE_API_URL` | Backend API URL (default: `http://localhost:8000`) | No |

## Deployment

### Backend (Railway)

1. Create a new Railway project
2. Connect your GitHub repository
3. Set the root directory to `backend`
4. Add environment variable: `ANTHROPIC_API_KEY`
5. Add environment variable: `FRONTEND_URL` (your Vercel frontend URL)
6. Deploy

### Frontend (Vercel)

1. Import your GitHub repository in Vercel
2. Set the root directory to `frontend`
3. Framework preset: Vite
4. Add environment variable: `VITE_API_URL` (your Railway backend URL)
5. Deploy

## Security Checks

| Check | Description |
|---|---|
| SPF Authentication | Verifies sender authorization via SPF record |
| DKIM Authentication | Validates message integrity via DKIM signature |
| DMARC Authentication | Checks domain alignment policy |
| From/Reply-To Mismatch | Flags when reply address differs from sender |
| Display Name Spoofing | Detects brand impersonation in display names |
| Embedded URL Analysis | Scans all URLs for suspicious indicators |
| Attachment Risk | Flags executable and macro-enabled file types |
| Header Path Analysis | Examines mail routing for anomalies |
| Subject Line Analysis | Detects urgency keywords and manipulation tactics |
| AI Analyst Verdict | Claude AI synthesizes all findings into a verdict |
