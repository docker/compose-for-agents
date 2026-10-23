FROM python:3.13-slim-trixie
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && \
    dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge '20250419+deb13u1' && \
    rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir 'pip>=26.2.2'

WORKDIR /app

# Create user first
RUN adduser --disabled-password --gecos "" myuser

# Copy requirements and install as root (so packages are available system-wide)
COPY requirements.txt .
RUN pip install --no-cache-dir 'certifi>=2026.10.19' -r requirements.txt

# Copy all files and change ownership in one step
COPY . .
RUN chown -R myuser:myuser /app

# Switch to non-root user
USER myuser

ENV PATH="/home/myuser/.local/bin:$PATH"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]