# Use an official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/dockeruser \
    PATH="/home/dockeruser/.local/bin:$PATH" \
    # Explicit cache paths to avoid permission issues
    HF_HOME=/home/dockeruser/.cache/huggingface \
    WHISPER_CACHE_DIR=/home/dockeruser/.cache/whisper

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    build-essential \
    ffmpeg \
    libsndfile1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create group and user with explicit UID/GID (match host)
RUN groupadd -g 1001 chl_ai && \
    useradd -u 1000 -g chl_ai -m -s /bin/bash dockeruser && \
    # Create cache directories with correct permissions
    mkdir -p /home/dockeruser/.cache/{huggingface,whisper} && \
    chown -R dockeruser:chl_ai /home/dockeruser/.cache

# Upgrade pip and configure (global)
RUN pip install --upgrade pip setuptools wheel && \
    mkdir -p /root/.pip && \
    echo "[global]\ntimeout = 100\nretries = 10" > /root/.pip/pip.conf

# Set work directory and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --default-timeout=100 -r requirements.txt

# Download spaCy model (as root, then fix permissions)
RUN python -m spacy download en_core_web_md && \
    chown -R dockeruser:chl_ai /home/dockeruser/.cache

# Copy project files and set permissions
COPY . .
RUN chown -R dockeruser:chl_ai /app

# Switch to dockeruser and configure user-level pip
USER dockeruser
RUN mkdir -p /home/dockeruser/.pip && \
    echo "[global]\ntimeout = 100\nretries = 10" > /home/dockeruser/.pip/pip.conf

# Expose port and run app
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers=4", "--threads=2", "--timeout=300", "ai_service.wsgi:application"]