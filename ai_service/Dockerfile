FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including curl for health checks and audio libraries)
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

# Create necessary directories
RUN mkdir -p /app/models /app/logs /app/temp \
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

# Create __init__.py files
RUN touch /app/app/__init__.py \
    && touch /app/app/core/__init__.py \
    && touch /app/app/api/__init__.py \
    && touch /app/app/model_scripts/__init__.py \
    && touch /app/app/config/__init__.py \
    && touch /app/app/tasks/__init__.py

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8123

# Health check for FastAPI
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8123/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8123"]