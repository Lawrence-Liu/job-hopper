from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool


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


def _run_enhancement(job_desc: str, original_resume: str, model: str) -> Any:
    try:
        from .workflow import ResumeLangGraphRunner

        result = ResumeLangGraphRunner(model=model).run(
            job_desc=job_desc,
            original_resume=original_resume,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"langgraph execution failed: {e}")

    enhanced_raw = result.get("enhanced_resume")
    if enhanced_raw is None:
        raise HTTPException(
            status_code=500,
            detail="Enhanced resume not produced. Check workflow and LLM credentials.",
        )

    if isinstance(enhanced_raw, str):
        try:
            return json.loads(enhanced_raw)
        except json.JSONDecodeError:
            return enhanced_raw
    return enhanced_raw


@app.post("/enhance", response_model=EnhanceResponse)
async def enhance(payload: EnhanceRequest) -> EnhanceResponse:
    enhanced = await run_in_threadpool(
        _run_enhancement,
        payload.job_description,
        payload.resume,
        payload.model,
    )
    return EnhanceResponse(enhanced_resume=enhanced, source="langgraph")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
