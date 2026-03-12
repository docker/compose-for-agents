FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1

RUN pip install uv

WORKDIR /app
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    uv pip install --system .
COPY agent.py .

COPY <<EOF /entrypoint.sh
#!/bin/sh
set -e
if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi
if test -n "${OPENAI_API_KEY}"; then
    echo "Using OpenAI with ${OPENAI_MODEL_NAME}"
    export MODEL_BASE_URL=https://api.openai.com/v1
    export MODEL_NAME=${OPENAI_MODEL_NAME}
else
    echo "Using Docker Model Runner with ${MODEL_RUNNER_MODEL}"
    export MODEL_BASE_URL=${MODEL_RUNNER_URL}
    export MODEL_NAME=${MODEL_RUNNER_MODEL}
    export OPENAI_API_KEY=cannot_be_empty
fi
exec python agent.py
EOF
RUN chmod +x /entrypoint.sh

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

ENTRYPOINT ["/entrypoint.sh"]
