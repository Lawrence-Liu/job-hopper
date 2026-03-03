# Resume Generator (CrewAI + LangGraph)

This project provides two implementations of the same resume enhancement pipeline:

- CrewAI version (existing implementation)
- LangGraph version (latest LangChain API + LangGraph orchestration)

Code is now physically separated under:

- `src/apps/crewai/`
- `src/apps/langgraph/`

Dependency environments are managed as two subprojects:

- `deploy/crewai/pyproject.toml` + `deploy/crewai/uv.lock`
- `deploy/langgraph/pyproject.toml` + `deploy/langgraph/uv.lock`

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, create two separate UV environments (dual-environment setup):

```bash
# CrewAI environment
cd deploy/crewai
UV_PROJECT_ENVIRONMENT=../../.venv-crewai uv sync --frozen

# LangGraph environment
cd ../langgraph
UV_PROJECT_ENVIRONMENT=../../.venv-agent uv sync --frozen
```

Activate the one you want before running commands.
### Customizing

Set model credentials per framework:

- CrewAI: add `OPENAI_API_KEY` in `.env` (or your CrewAI model provider vars)
- LangGraph (Gemini via Google GenAI): set `GOOGLE_API_KEY` in your environment

- Modify `src/apps/crewai/config/agents.yaml` to define your agents
- Modify `src/apps/crewai/config/tasks.yaml` to define your tasks
- Modify `src/apps/crewai/crew.py` to add your own logic, tools and specific args
- CrewAI runtime entry: `src/apps/crewai/main.py`
- LangGraph runtime entry: `src/apps/langgraph/main.py`

## Running the Project

To kickstart your agents and begin task execution, run these from the repo root:

### 1) CrewAI version

```bash
cd deploy/crewai
UV_PROJECT_ENVIRONMENT=../../.venv-crewai PYTHONPATH=../../src uv run --project . python -c "from apps.crewai.main import run; run('../../jobs/red-venture-ds-group-manager', '../../Lawrence_Resume.json')"
```

### 2) LangGraph version (latest)

```bash
cd deploy/langgraph
UV_PROJECT_ENVIRONMENT=../../.venv-agent PYTHONPATH=../../src uv run --project . python -c "from apps.langgraph.main import run; run('../../jobs/red-venture-ds-group-manager', '../../Lawrence_Resume.json')"
```

Both versions generate:

- `jobs/<target_job>/enhanced_resume.json`
- `jobs/<target_job>/styled_resume.md`

### API (fully separate)

- CrewAI API app: `apps.crewai.api:app`
- LangGraph API app: `apps.langgraph.api:app`

Run CrewAI API:

```bash
cd deploy/crewai
UV_PROJECT_ENVIRONMENT=../../.venv-crewai uv run --project . python -m uvicorn apps.crewai.api:app --reload --port 8000 --app-dir ../../src
```

Run LangGraph API:

```bash
cd deploy/langgraph
UV_PROJECT_ENVIRONMENT=../../.venv-agent uv run --project . python -m uvicorn apps.langgraph.api:app --reload --port 8001 --app-dir ../../src
```

## Frontend (minimal)

A minimal frontend is available at `frontend/index.html`.

Run locally from repo root:

```bash
python -m http.server 5500
```

Then open:

- `http://localhost:5500/frontend/`

Set API Base URL to your Cloud Run URL (or local API URL), paste job description and resume, then click **Enhance Resume**.

## Understanding Your Crew

The resume-generator Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `src/apps/crewai/config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `src/apps/crewai/config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the ResumeGenerator Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
