FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1001 chl_ai && \
    useradd -u 1000 -g chl_ai -m -s /bin/bash dockeruser

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Improve pip resilience
RUN mkdir -p /root/.pip && \
    echo "[global]\ntimeout = 100\nretries = 10" > /root/.pip/pip.conf

WORKDIR /app
RUN chown dockeruser:chl_ai /app

# Copy requirements and full codebase in one go
COPY . .

# Install Python dependencies
RUN pip install --default-timeout=100 -r requirements.txt

# Install spaCy model
RUN python -m spacy download en_core_web_md

# Set ownership
RUN chown -R dockeruser:chl_ai /app

USER dockeruser

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "ai_service.asgi:application"]
