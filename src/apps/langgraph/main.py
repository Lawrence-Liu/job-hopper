#!/usr/bin/env python

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _resolve_from_project_root(path_like: str | Path) -> Path:
    path = Path(path_like)
    return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def run(job_folder: str, original_resume: str, model: str = "gemini-2.5-flash"):
    job_folder_path = _resolve_from_project_root(job_folder)
    print(job_folder_path)
    resume_path = _resolve_from_project_root(original_resume)
    jd_path = job_folder_path / "jd.txt"

    with jd_path.open("r", encoding="utf-8") as f:
        job_desc_content = f.read()
    with resume_path.open("r", encoding="utf-8") as f:
        original_resume_content = f.read()

    try:
        try:
            from .workflow import ResumeLangGraphRunner
        except ImportError:
            from workflow import ResumeLangGraphRunner

        ResumeLangGraphRunner(model=model).run(
            job_desc=job_desc_content,
            original_resume=original_resume_content,
            enhanced_resume_path=str(job_folder_path / "enhanced_resume.json"),
            styled_resume_path=str(job_folder_path / "styled_resume.md"),
        )
    except Exception as e:
        raise Exception(f"An error occurred while running langgraph flow: {e}")


if __name__ == "__main__":
    job_folder = "jobs/red-venture-ds-group-manager"
    original_resume = "Lawrence_Resume.json"
    run(job_folder, original_resume)
