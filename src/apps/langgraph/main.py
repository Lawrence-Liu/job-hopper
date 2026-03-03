#!/usr/bin/env python


def run(job_folder: str, original_resume: str, model: str = "gpt-5-mini"):
    jd_path = f"{job_folder}/jd.txt"
    with open(jd_path, "r", encoding="utf-8") as f:
        job_desc_content = f.read()
    with open(original_resume, "r", encoding="utf-8") as f:
        original_resume_content = f.read()

    try:
        from .workflow import ResumeLangGraphRunner

        ResumeLangGraphRunner(model=model).run(
            job_desc=job_desc_content,
            original_resume=original_resume_content,
            enhanced_resume_path=f"{job_folder}/enhanced_resume.json",
            styled_resume_path=f"{job_folder}/styled_resume.md",
        )
    except Exception as e:
        raise Exception(f"An error occurred while running langgraph flow: {e}")


if __name__ == "__main__":
    job_folder = "./jobs/red-venture-ds-group-manager"
    original_resume = "./Lawrence_Resume.json"
    run(job_folder, original_resume)
