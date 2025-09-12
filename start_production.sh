#!/bin/bash

# Healthcare Chatbot Production Startup Script for Render
echo "🏥 Starting Healthcare Chatbot Production Server..."

# Set environment variables
export PYTHONPATH=/app
export RASA_TELEMETRY_ENABLED=false

# Function to check if service is running
wait_for_service() {
    local port=$1
    local service_name=$2
    local timeout=60
    local count=0
    
    echo "⏳ Waiting for $service_name to start on port $port..."
    
    while ! nc -z localhost $port; do
        sleep 2
        count=$((count + 2))
        if [ $count -ge $timeout ]; then
            echo "❌ $service_name failed to start within $timeout seconds"
            return 1
        fi
    done
    
    echo "✅ $service_name is running on port $port"
    return 0
}

# Kill any existing processes
pkill -f "rasa run" || true
pkill -f "rasa run actions" || true
sleep 2

# Check if model exists, train if not
if [ ! -d "/app/models" ] || [ -z "$(ls -A /app/models)" ]; then
    echo "📚 Training Rasa model..."
    cd /app
    rasa train --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Model training failed"
        exit 1
    fi
    echo "✅ Model training completed"
else
    echo "✅ Using existing trained model"
fi

# Start Action Server in background
echo "🚀 Starting Action Server..."
cd /app
nohup rasa run actions --port 5055 --debug > /app/logs/actions.log 2>&1 &
ACTION_PID=$!

# Wait for Action Server to be ready
if ! wait_for_service 5055 "Action Server"; then
    echo "❌ Action Server failed to start"
    exit 1
fi

# Start Rasa Server
echo "🤖 Starting Rasa Server..."
cd /app

# Start Rasa server with API enabled and CORS
exec rasa run \
    --port 5005 \
    --enable-api \
    --cors "*" \
    --auth-token "${RASA_AUTH_TOKEN:-}" \
    --debug
