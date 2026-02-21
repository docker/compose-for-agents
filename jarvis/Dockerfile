FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install timezone data (needed for zoneinfo)
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

# Create notes volume mount point
RUN mkdir -p /data/notes

VOLUME ["/data/notes"]

# Entrypoint: resolve API key from secret file or env var, then launch agent
COPY <<'EOF' /entrypoint.sh
#!/bin/sh
set -e

# Docker secrets take precedence
if [ -f /run/secrets/anthropic-api-key ]; then
    export ANTHROPIC_API_KEY=$(cat /run/secrets/anthropic-api-key)
fi

if [ -z "${ANTHROPIC_API_KEY}" ]; then
    echo "ERROR: ANTHROPIC_API_KEY is required."
    echo "  Option 1: Set ANTHROPIC_API_KEY environment variable"
    echo "  Option 2: Create 'secret.anthropic-api-key' with your key"
    exit 1
fi

exec python agent.py
EOF

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
