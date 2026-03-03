FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN pip install --no-cache-dir uv==0.8.4

COPY deploy/langgraph/pyproject.toml /app/pyproject.toml
COPY deploy/langgraph/uv.lock /app/uv.lock
COPY src/apps /app/src/apps

RUN uv export --frozen --no-dev --format requirements-txt > /tmp/requirements.txt \
    && uv pip install --system --no-cache -r /tmp/requirements.txt

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn apps.langgraph.api:app --host 0.0.0.0 --port ${PORT}"]
