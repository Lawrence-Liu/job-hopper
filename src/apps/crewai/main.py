#!/usr/bin/env python
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run(job_folder: str, original_resume: str):
    jd_path = f"{job_folder}/jd.txt"
    with open(jd_path, "r", encoding="utf-8") as f:
        job_desc_content = f.read()
    with open(original_resume, "r", encoding="utf-8") as f:
        original_resume_content = f.read()

    inputs = {
        "job_desc": job_desc_content,
        "original_resume": original_resume_content,
        "enhanced_resume_path": f"{job_folder}/enhanced_resume.json",
        "styled_resume_path": f"{job_folder}/styled_resume.md",
    }

    try:
        from .crew import ResumeGenerator

        ResumeGenerator().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}
    try:
        from .crew import ResumeGenerator

        ResumeGenerator().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    try:
        from .crew import ResumeGenerator

        ResumeGenerator().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}
    try:
        from .crew import ResumeGenerator

        ResumeGenerator().crew().test(
            n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
