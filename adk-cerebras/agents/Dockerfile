FROM python:3.13-slim

WORKDIR /app

# Create user first
RUN adduser --disabled-password --gecos "" myuser

# Copy requirements and install as root (so packages are available system-wide)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files and change ownership in one step
COPY . .
RUN chown -R myuser:myuser /app

# Switch to non-root user
USER myuser

ENV PATH="/home/myuser/.local/bin:$PATH"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]