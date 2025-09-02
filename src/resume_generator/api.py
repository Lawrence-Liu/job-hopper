from __future__ import annotations

import asyncio
import json
import os
import tempfile
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .crew import ResumeGenerator


app = FastAPI(title="Resume Generator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for specific frontend
    allow_credentials=True,
    allow_methods=["*"],   # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],   # allow Authorization, Content-Type, etc.
)

# Ensure requests that rely on CWD output files do not step on each other
_run_lock = asyncio.Lock()


class EnhanceRequest(BaseModel):
    job_description: str = Field(..., description="Job description text")
    resume: str = Field(..., description="Original resume text (can be JSON string)")


class EnhanceResponse(BaseModel):
    enhanced_resume: Any
    source: str


def _read_enhanced_resume_file(base_dir: str) -> Optional[Any]:
    """Read enhanced resume from known file locations relative to base_dir.

    Returns parsed JSON if possible, otherwise raw text.
    """
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
    """Run the crew to enhance the resume and return the enhanced resume.

    This uses a temp working directory so that task outputs (e.g., enhanced_resume.json)
    are isolated per request.
    """
    # Prepare inputs
    inputs: Dict[str, Any] = {
        "job_desc": job_desc,
        "original_resume": original_resume,
    }

    # Run crew in isolated temp CWD to capture output files safely
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            # Kick off the crew synchronously; CrewAI API is sync
            ResumeGenerator().crew().kickoff(inputs=inputs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Crew execution failed: {e}")
        finally:
            os.chdir(orig_cwd)

        # Try to read the enhanced resume file
        enhanced = _read_enhanced_resume_file(tmpdir)
        if enhanced is None:
            # As a fallback, surface a clear error
            raise HTTPException(
                status_code=500,
                detail=(
                    "Enhanced resume file not produced. Check task configuration "
                    "and LLM credentials."
                ),
            )
        return enhanced


@app.post("/enhance", response_model=EnhanceResponse)
async def enhance(payload: EnhanceRequest) -> EnhanceResponse:
    # Serialize calls to avoid race conditions with global resources
    async with _run_lock:
        enhanced = await _run_enhancement(
            job_desc=payload.job_description, original_resume=payload.resume
        )
    return EnhanceResponse(enhanced_resume=enhanced, source="crewai")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}

