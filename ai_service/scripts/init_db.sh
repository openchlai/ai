#!/bin/bash
# Database initialization script for Docker containers
# Ensures database directory exists with proper permissions

echo "🔧 Initializing database directory..."

# Create database directory if it doesn't exist
mkdir -p /app/db

# Set permissions to allow write access
chmod 777 /app/db

# Check if database file exists
if [ -f "/app/db/ai_service.db" ]; then
    echo "✅ Database file already exists at /app/db/ai_service.db"
    chmod 666 /app/db/ai_service.db
else
    echo "📝 Database file will be created on first use at /app/db/ai_service.db"
fi

echo "✅ Database directory initialized successfully"
