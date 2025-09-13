#!/bin/bash

# Healthcare Chatbot - Ultra Minimal Startup for Render
echo "🏥 Starting Healthcare Chatbot (Ultra Minimal)..."

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

# Try to train model, but don't fail if it doesn't work
if [ ! -d "/app/models" ] || [ -z "$(ls -A /app/models)" ]; then
    echo "📚 Attempting to train model..."
    
    # Try ultra-minimal training with timeout
    timeout 180 rasa train --config config-minimal.yml --domain domain.yml --data data --out models --quiet 2>/dev/null || {
        echo "⚠️ Training failed or timed out after 3 minutes"
        echo "🚀 Starting without trained model (will use rules only)"
    }
fi

# Start Rasa server regardless of training success
echo "🤖 Starting Rasa Server..."
echo "🔗 Server will be accessible at http://0.0.0.0:$PORT"

# Start Rasa server with correct syntax (using -i for interface instead of --interface)
exec rasa run \
    -p $PORT \
    -i 0.0.0.0 \
    --enable-api \
    --cors "*" \
    --debug
