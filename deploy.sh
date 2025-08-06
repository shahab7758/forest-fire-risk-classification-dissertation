#!/bin/bash

echo "🚀 Starting deployment process..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t forest-fire-app .

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker stop forest-fire-container 2>/dev/null || true
docker rm forest-fire-container 2>/dev/null || true

# Run the container
echo "▶️ Starting the application..."
docker run -d \
    --name forest-fire-container \
    -p 5000:5000 \
    --env-file .env \
    forest-fire-app

echo "✅ Deployment complete!"
echo "🌐 Your app is running at: http://localhost:5000"
echo "📊 To view logs: docker logs forest-fire-container"
echo "🛑 To stop: docker stop forest-fire-container" 