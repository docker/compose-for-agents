##### Base image
FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1
RUN pip install uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    uv pip install --system .
COPY main.py src ./
RUN python -m compileall -q .

ENV AGENT_CONFIG=/app/agent.yaml

COPY <<EOF ./entrypoint.sh
#!/bin/sh
set -e

if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi

if test -n "\${OPENAI_API_KEY}"; then
    echo "Using OpenAI with \${MODEL_NAME}"
    export LLM_AGENT_MODEL_PROVIDER=openai
    export LLM_AGENT_MODEL_NAME=\${OPENAI_MODEL_NAME}
else
    echo "Using Docker Model Runner with \${MODEL_RUNNER_MODEL}"
    export LLM_AGENT_MODEL_PROVIDER=docker
    export LLM_AGENT_MODEL_NAME=\${MODEL_RUNNER_MODEL}
fi
exec \$@
EOF
RUN chmod +x ./entrypoint.sh

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

##### Critic Agent
FROM base AS critic-agent

COPY --chown=app:app agents/critic.yaml /app/agent.yaml
CMD ["./entrypoint.sh", "python", "main.py", "--host", "0.0.0.0", "--port", "8001"]

##### Reviser Agent
FROM base AS reviser-agent

COPY --chown=app:app agents/reviser.yaml /app/agent.yaml
CMD ["./entrypoint.sh", "python", "main.py", "--host", "0.0.0.0", "--port", "8001"]

##### Auditor Agent
FROM base AS auditor-agent

COPY --chown=app:app agents/auditor.yaml /app/agent.yaml
EXPOSE 8080
CMD ["./entrypoint.sh", "adk", "web", ".", "--host", "0.0.0.0", "--port", "8080"]
# Use this to expose the agent as a web service instead of a UI
#CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8002"]
