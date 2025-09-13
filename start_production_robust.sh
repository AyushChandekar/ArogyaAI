#!/bin/bash

# Healthcare Chatbot - Robust Startup for Render
echo "🏥 Starting Healthcare Chatbot (Robust with Fallback)..."

# Set environment variables
export PYTHONPATH=/app
export RASA_TELEMETRY_ENABLED=false
export PYTHONUNBUFFERED=1
export TF_CPP_MIN_LOG_LEVEL=3
export PYTHONDONTWRITEBYTECODE=1

cd /app

# Use Render's PORT environment variable or default to 10000
PORT=${PORT:-10000}
echo "🌐 Will bind to host 0.0.0.0 on port $PORT"

# Function to start fallback server
start_fallback() {
    echo "🔄 Starting fallback Flask server..."
    exec python3 simple_server.py
}

# Function to try Rasa startup
try_rasa() {
    echo "📚 Attempting to train Rasa model..."
    
    # Check if basic files exist
    if [ ! -f "domain.yml" ] || [ ! -f "config-minimal.yml" ] || [ ! -d "data" ]; then
        echo "⚠️ Missing required Rasa files. Starting fallback server."
        start_fallback
        return 1
    fi
    
    # Try training with timeout
    if timeout 180 rasa train --config config-minimal.yml --domain domain.yml --data data --out models --quiet 2>/dev/null; then
        echo "✅ Model training successful!"
    else
        echo "⚠️ Training failed or timed out after 3 minutes"
        echo "🚀 Will try to start Rasa without trained model"
    fi
    
    # Try to start Rasa server
    echo "🤖 Starting Rasa Server..."
    echo "🔗 Server will be accessible at http://0.0.0.0:$PORT"
    
    # Start Rasa with timeout to detect startup issues
    timeout 30 rasa run \
        -p $PORT \
        -i 0.0.0.0 \
        --enable-api \
        --cors "*" \
        --debug &
    
    RASA_PID=$!
    
    # Wait a bit and check if Rasa is still running
    sleep 10
    if kill -0 $RASA_PID 2>/dev/null; then
        echo "✅ Rasa server started successfully"
        # Wait for Rasa process
        wait $RASA_PID
    else
        echo "❌ Rasa server failed to start properly"
        return 1
    fi
}

# Try Rasa first, fallback to simple server if it fails
if ! try_rasa; then
    echo "🔄 Rasa startup failed, switching to fallback server"
    start_fallback
fi