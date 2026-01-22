FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including curl for health checks, audio libraries, and SCP tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    gcc \
    portaudio19-dev \
    python3-dev \
    ffmpeg \
    libsndfile1 \
    libsox-fmt-all \
    sox \
    sshpass \
    openssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache

# Create non-root user
RUN groupadd -g 1000 appuser && useradd -r -u 1000 -g appuser appuser

# Create necessary directories including HuggingFace cache
RUN mkdir -p /app/models /app/logs /app/temp /app/.cache/huggingface \
    && chown -R appuser:appuser /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge \
    && rm -rf /root/.cache/pip

# Copy models into container (container-baked approach)
COPY models/ /app/models/

# Copy application code
COPY app/ /app/app/

# Create __init__.py files for Python packages
RUN touch /app/app/__init__.py \
    && touch /app/app/core/__init__.py \
    && touch /app/app/api/__init__.py \
    && touch /app/app/model_scripts/__init__.py \
    && touch /app/app/config/__init__.py \
    && touch /app/app/tasks/__init__.py \
    && touch /app/app/utils/__init__.py \
    && touch /app/app/services/__init__.py \
    && touch /app/app/streaming/__init__.py \
    && touch /app/app/db/__init__.py

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports (configurable via env vars, defaults: 8125 for API, 8300 for streaming)
EXPOSE ${APP_PORT:-8125} ${STREAMING_PORT:-8300}

# Health check for FastAPI (uses APP_PORT env var)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${APP_PORT:-8125}/health || exit 1

# Default command (can be overridden in docker-compose)
# Note: This is overridden by docker-compose, which uses app.main startup
CMD ["python", "-m", "app.main"]