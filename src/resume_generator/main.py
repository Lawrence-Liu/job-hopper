#!/usr/bin/env python
import sys
import warnings

from resume_generator.crew import ResumeGenerator

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run(desc_file: str, original_resume: str):
    """
    Run the crew.
    """
    with open(desc_file, "r", encoding="utf-8") as f:
        job_desc_content = f.read()
    with open(original_resume, "r", encoding="utf-8") as f:
        original_resume_content = f.read()
    inputs = {
        'job_desc': job_desc_content,
        'original_resume': original_resume_content
    }
    
    try:
        ResumeGenerator().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        ResumeGenerator().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ResumeGenerator().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        ResumeGenerator().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    jd_file = '/Users/lawrence/Projects/resume-generator/JD/wells-fargo-gen-ai-principal-engineer.txt'
    original_resume = '/Users/lawrence/Projects/resume-generator/Lawrence_Resume.json'
    run(jd_file, original_resume)
    
