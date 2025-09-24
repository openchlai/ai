#!/bin/bash

# Build and deploy script for wallboard application

echo "🚀 Starting wallboard build and deployment..."

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found!"
    exit 1
fi

# Build Docker image
echo "📦 Building Docker image..."
docker build -t wallboard:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully!"

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker-compose down

# Start the application
echo "🚀 Starting wallboard application..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Wallboard is now running!"
    echo "🌐 Access your wallboard at: http://localhost:8080"
    echo "📊 Health check: http://localhost:8080/health"
else
    echo "❌ Failed to start the application!"
    exit 1
fi

# Show container status
echo "📋 Container status:"
docker-compose ps