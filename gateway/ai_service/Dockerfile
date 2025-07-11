# Use an official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    build-essential \
    ffmpeg \
    libsndfile1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create group and user matching host chl_ai group
# IMPORTANT: Replace 1001 with your actual chl_ai group ID
RUN groupadd -g 1001 chl_ai && \
    useradd -u 1000 -g chl_ai -m -s /bin/bash dockeruser

# Upgrade pip, setuptools, wheel first to avoid build failures
RUN pip install --upgrade pip setuptools wheel

# Increase pip timeout and retries
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 100" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf

# Set work directory and change ownership
WORKDIR /app
RUN chown dockeruser:chl_ai /app

# Install Python dependencies as root (for system packages)
COPY requirements.txt .
RUN pip install --default-timeout=100 -r requirements.txt

# Download spaCy medium language model (larger and better than sm)
RUN python -m spacy download en_core_web_md

# Copy the rest of the project files
COPY . .
RUN chown -R dockeruser:chl_ai /app

# Ensure gunicorn is available in the system PATH
RUN which gunicorn || echo "Gunicorn not found"

# Switch to dockeruser
USER dockeruser

# Expose port
EXPOSE 8000

# Run Django app with Gunicorn
# Replace 'your_project_name' with the actual project folder name
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers=4", "--threads=2", "--timeout=300", "ai_service.wsgi:application"]
