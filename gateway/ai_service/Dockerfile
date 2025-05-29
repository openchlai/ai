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
    && rm -rf /var/lib/apt/lists/*

# Create group and user matching host chl_ai group
# IMPORTANT: Replace 1001 with your actual chl_ai group ID
# Get it with: getent group chl_ai | cut -d: -f3
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

# Download spaCy language model
RUN python -m spacy download en_core_web_sm

# Copy the rest of the project files
COPY . .
RUN chown -R dockeruser:chl_ai /app

# Switch to dockeruser
USER dockeruser

# Set up user pip config
RUN mkdir -p /home/dockeruser/.pip && \
    echo "[global]" > /home/dockeruser/.pip/pip.conf && \
    echo "timeout = 100" >> /home/dockeruser/.pip/pip.conf && \
    echo "retries = 10" >> /home/dockeruser/.pip/pip.conf

# Set environment variables for user
ENV HOME=/home/dockeruser
ENV PATH="/home/dockeruser/.local/bin:$PATH"

# Expose port
EXPOSE 8000

# Run Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]