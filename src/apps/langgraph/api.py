from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(title="Resume Generator LangGraph API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EnhanceRequest(BaseModel):
    job_description: str = Field(..., description="Job description text")
    resume: str = Field(..., description="Original resume text (can be JSON string)")
    model: str = Field(default="gemini-2.5-flash", description="Model name for LangGraph workflow")


class EnhanceResponse(BaseModel):
    enhanced_resume: Any
    source: str


@app.post("/enhance", response_model=EnhanceResponse)
async def enhance(payload: EnhanceRequest) -> EnhanceResponse:
    try:
        from .workflow import ResumeLangGraphRunner

        result = await ResumeLangGraphRunner(model=payload.model).arun(
            job_desc=payload.job_description,
            original_resume=payload.resume,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"langgraph execution failed: {e}")

    enhanced_raw = result.get("enhanced_resume")
    if enhanced_raw is None:
        raise HTTPException(
            status_code=500,
            detail="Enhanced resume not produced. Check workflow and LLM credentials.",
        )

    enhanced = enhanced_raw
    if isinstance(enhanced_raw, str):
        try:
            enhanced = json.loads(enhanced_raw)
        except json.JSONDecodeError:
            pass

    return EnhanceResponse(enhanced_resume=enhanced, source="langgraph")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
