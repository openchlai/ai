# Base image
FROM python:3.10-slim

# Avoid writing .pyc files and force unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set environment variables for socket server (optional defaults)
ENV TCP_HOST=0.0.0.0
ENV TCP_PORT=8300

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1001 chl_ai && \
    useradd -u 1000 -g chl_ai -m -s /bin/bash dockeruser

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Improve pip resilience
RUN mkdir -p /root/.pip && \
    echo "[global]\ntimeout = 100\nretries = 10" > /root/.pip/pip.conf

# Set working directory
WORKDIR /app
RUN chown dockeruser:chl_ai /app

# Copy all code
COPY . .

# Install Python dependencies
RUN pip install --default-timeout=100 -r requirements.txt

# Install spaCy model (or add others as needed)
RUN python -m spacy download en_core_web_md

# Set ownership again in case COPY reset it
RUN chown -R dockeruser:chl_ai /app

# Switch to non-root user
USER dockeruser

# Expose HTTP port (Daphne) and audio socket port
EXPOSE 8000
EXPOSE 8300

# Default command is to launch the Django ASGI app with Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "ai_service.asgi:application"]
