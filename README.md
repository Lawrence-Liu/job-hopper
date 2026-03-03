# Resume Generator (CrewAI + LangGraph)

This project provides two implementations of the same resume enhancement pipeline:

- CrewAI version (existing implementation)
- LangGraph version (latest LangChain API + LangGraph orchestration)

Code is now physically separated under:

- `src/apps/crewai/`
- `src/apps/langgraph/`

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, create two separate UV environments (dual-environment setup):

```bash
# CrewAI environment
UV_PROJECT_ENVIRONMENT=.venv-crewai uv sync

# LangGraph environment
uv venv .venv-agent
UV_PROJECT_ENVIRONMENT=.venv-agent uv pip install -r requirements/create-agent.txt
UV_PROJECT_ENVIRONMENT=.venv-agent uv pip install -e . --no-deps
```

Activate the one you want before running commands.
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/apps/crewai/config/agents.yaml` to define your agents
- Modify `src/apps/crewai/config/tasks.yaml` to define your tasks
- Modify `src/apps/crewai/crew.py` to add your own logic, tools and specific args
- CrewAI runtime entry: `src/apps/crewai/main.py`
- LangGraph runtime entry: `src/apps/langgraph/main.py`

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

### 1) CrewAI version

```bash
UV_PROJECT_ENVIRONMENT=.venv-crewai uv run python -c "from apps.crewai.main import run; run('./jobs/red-venture-ds-group-manager', './Lawrence_Resume.json')"
```

### 2) LangGraph version (latest)

```bash
UV_PROJECT_ENVIRONMENT=.venv-agent uv run python -c "from apps.langgraph.main import run; run('./jobs/red-venture-ds-group-manager', './Lawrence_Resume.json')"
```

Both versions generate:

- `jobs/<target_job>/enhanced_resume.json`
- `jobs/<target_job>/styled_resume.md`

### API (fully separate)

- CrewAI API app: `apps.crewai.api:app`
- LangGraph API app: `apps.langgraph.api:app`

Run CrewAI API:

```bash
UV_PROJECT_ENVIRONMENT=.venv-crewai uv run uvicorn apps.crewai.api:app --reload --port 8000
```

Run LangGraph API:

```bash
UV_PROJECT_ENVIRONMENT=.venv-agent uv run uvicorn apps.langgraph.api:app --reload --port 8001
```

## Understanding Your Crew

The resume-generator Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `apps/crewai/config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `apps/crewai/config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the ResumeGenerator Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
