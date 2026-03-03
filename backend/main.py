import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from analyzer import analyze_eml
from ai_verdict import get_ai_verdict

load_dotenv()

app = FastAPI(title="SafeMail API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store: result_id -> analysis result
results_store: dict[str, dict] = {}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".eml"):
        raise HTTPException(status_code=400, detail="Please upload a .eml file")

    contents = await file.read()
    eml_text = contents.decode("utf-8", errors="replace")

    analysis = analyze_eml(eml_text)

    ai_result = get_ai_verdict(analysis)
    analysis["ai_verdict"] = ai_result

    risk_score = calculate_risk_score(analysis)
    analysis["risk_score"] = risk_score
    analysis["risk_verdict"] = get_risk_verdict(risk_score)

    result_id = str(uuid.uuid4())
    analysis["id"] = result_id
    analysis["filename"] = file.filename

    results_store[result_id] = analysis

    return analysis


@app.get("/api/history")
def history():
    summaries = []
    for r in reversed(list(results_store.values())):
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
def get_result(analysis_id: str):
    result = results_store.get(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


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
