from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agents.graph import run_investigation

app = FastAPI(
    title="AI Security Detection & Response Copilot",
    version="0.1.0",
    description="Local investigation copilot with guardrails, retrieval, and an audit trail.",
)


class InvestigateRequest(BaseModel):
    alert: str = Field(min_length=1, max_length=8000)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/investigate")
def investigate(req: InvestigateRequest) -> dict:
    return run_investigation(req.alert).as_dict()
