FROM python:3.13-slim-trixie
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && \
    dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge '20250419+deb13u1' && \
    rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir 'pip>=26.2.2'
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    socat \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv==0.13.4

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1 uv pip install --system .
COPY playground.py .
RUN python -m compileall -q .
COPY <<EOF entrypoint.sh
#!/bin/sh

if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi

if test -n "\${OPENAI_API_KEY}"; then
    echo "Using OpenAI with \${OPENAI_MODEL_NAME}"
    export MODEL_PROVIDER=openai
    export MODEL_NAME=\${OPENAI_MODEL_NAME}
else
    echo "Using Docker Model Runner with \${MODEL_RUNNER_MODEL}"
    export MODEL_PROVIDER=docker
    export MODEL_NAME=\${MODEL_RUNNER_MODEL}
    export OPENAI_API_KEY=cannot_be_empty
fi
exec python playground.py
EOF
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
