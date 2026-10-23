# Use Python 3.13 slim image as base
FROM python:3.13-slim-trixie
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && \
    dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge '20250419+deb13u1' && \
    rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir 'pip>=26.2.2'
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN pip install --no-cache-dir uv==0.13.4

WORKDIR /app
# Install system dependencies
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    uv sync --locked --no-dev --no-install-project
# Copy application code
COPY agents/ ./agents/
RUN python -m compileall -q .

COPY <<EOF /entrypoint.sh
#!/bin/sh
set -e

# if test -f /run/secrets/openai-api-key; then
#     export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
# fi

# if test -n "\${OPENAI_API_KEY}"; then
#     echo "Using OpenAI with \${OPENAI_MODEL_NAME}"
# else
    echo "Using Docker Model Runner with \${MODEL_RUNNER_MODEL}"
    export OPENAI_MODEL_NAME=openai/\${MODEL_RUNNER_MODEL}
# fi
exec adk api_server --host 0.0.0.0 --port 8000 --log_level DEBUG
EOF
RUN chmod +x /entrypoint.sh

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

ENTRYPOINT [ "/entrypoint.sh" ]
