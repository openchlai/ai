# Use an official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel first to avoid build failures
RUN pip install --upgrade pip setuptools wheel

# Increase pip timeout and retries
RUN mkdir -p ~/.pip && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "timeout = 100" >> ~/.pip/pip.conf && \
    echo "retries = 10" >> ~/.pip/pip.conf

# Install Python dependencies
COPY requirements.txt .
RUN pip install --default-timeout=100 -r requirements.txt

# Copy the rest of the project files
COPY . .

# Download spaCy language model
RUN python -m spacy download en_core_web_sm

# Expose port
EXPOSE 8000

# Run Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
