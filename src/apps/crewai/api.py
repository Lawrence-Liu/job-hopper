from __future__ import annotations

import asyncio
import json
import os
import tempfile
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(title="Resume Generator CrewAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_run_lock = asyncio.Lock()


class EnhanceRequest(BaseModel):
    job_description: str = Field(..., description="Job description text")
    resume: str = Field(..., description="Original resume text (can be JSON string)")


class EnhanceResponse(BaseModel):
    enhanced_resume: Any
    source: str


def _read_enhanced_resume_file(base_dir: str) -> Optional[Any]:
    candidates = [
        os.path.join(base_dir, "enhanced_resume.json"),
        os.path.join(base_dir, "src", "enhanced_resume.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return content
            except Exception:
                continue
    return None


async def _run_enhancement(job_desc: str, original_resume: str) -> Any:
    inputs: Dict[str, Any] = {"job_desc": job_desc, "original_resume": original_resume}

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            from .crew import ResumeGenerator

            ResumeGenerator().crew().kickoff(inputs=inputs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"crewai execution failed: {e}")
        finally:
            os.chdir(orig_cwd)

        enhanced = _read_enhanced_resume_file(tmpdir)
        if enhanced is None:
            raise HTTPException(
                status_code=500,
                detail="Enhanced resume file not produced. Check task configuration and LLM credentials.",
            )
        return enhanced


@app.post("/enhance", response_model=EnhanceResponse)
async def enhance(payload: EnhanceRequest) -> EnhanceResponse:
    async with _run_lock:
        enhanced = await _run_enhancement(
            job_desc=payload.job_description,
            original_resume=payload.resume,
        )
    return EnhanceResponse(enhanced_resume=enhanced, source="crewai")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
