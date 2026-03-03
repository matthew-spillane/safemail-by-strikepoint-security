import os
import uuid
from fastapi import FastAPI, UploadFile, File, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from analyzer import analyze_eml
from ai_verdict import get_ai_verdict

load_dotenv()

app = FastAPI(title="SafeMail API", version="1.0.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

allowed_origins = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
]

# Allow all Vercel preview/production URLs for this project
VERCEL_URL = os.getenv("VERCEL_URL", "")
if VERCEL_URL and VERCEL_URL not in allowed_origins:
    allowed_origins.append(VERCEL_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: session_id -> list of analysis results
sessions: dict[str, list[dict]] = {}

SESSION_COOKIE = "safemail_session"


def get_session_id(request: Request, response: Response) -> str:
    session_id = request.cookies.get(SESSION_COOKIE)
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key=SESSION_COOKIE,
            value=session_id,
            httponly=True,
            samesite="none",
            secure=True,
            max_age=60 * 60 * 24 * 7,
        )
    if session_id not in sessions:
        sessions[session_id] = []
    return session_id


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(request: Request, response: Response, file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".eml"):
        raise HTTPException(status_code=400, detail="Please upload a .eml file")

    session_id = get_session_id(request, response)
    contents = await file.read()
    eml_text = contents.decode("utf-8", errors="replace")

    analysis = analyze_eml(eml_text)

    ai_result = get_ai_verdict(analysis)
    analysis["ai_verdict"] = ai_result

    risk_score = calculate_risk_score(analysis)
    analysis["risk_score"] = risk_score
    analysis["risk_verdict"] = get_risk_verdict(risk_score)

    analysis["id"] = str(uuid.uuid4())
    analysis["filename"] = file.filename

    sessions[session_id].append(analysis)

    return analysis


@app.get("/api/history")
def history(request: Request, response: Response):
    session_id = get_session_id(request, response)
    results = sessions.get(session_id, [])
    summaries = []
    for r in reversed(results):
        summaries.append({
            "id": r["id"],
            "filename": r["filename"],
            "subject": r.get("subject", ""),
            "risk_score": r["risk_score"],
            "risk_verdict": r["risk_verdict"],
            "ai_verdict_label": r.get("ai_verdict", {}).get("verdict", "Unknown"),
            "sender": r.get("from", ""),
        })
    return summaries


@app.get("/api/results/{analysis_id}")
def get_result(analysis_id: str, request: Request, response: Response):
    session_id = get_session_id(request, response)
    results = sessions.get(session_id, [])
    for r in results:
        if r["id"] == analysis_id:
            return r
    raise HTTPException(status_code=404, detail="Result not found")


def calculate_risk_score(analysis: dict) -> int:
    score = 0
    checks = analysis.get("checks", [])
    for check in checks:
        status = check.get("status", "pass")
        if status == "fail":
            score += 15
        elif status == "warn":
            score += 8

    ai_verdict = analysis.get("ai_verdict", {}).get("verdict", "")
    if ai_verdict == "Phishing":
        score += 25
    elif ai_verdict == "Likely Phishing":
        score += 18
    elif ai_verdict == "Suspicious":
        score += 10
    elif ai_verdict == "Safe":
        score -= 5

    return max(0, min(100, score))


def get_risk_verdict(score: int) -> str:
    if score <= 20:
        return "Safe"
    elif score <= 45:
        return "Suspicious"
    elif score <= 70:
        return "Likely Phishing"
    else:
        return "Phishing"
