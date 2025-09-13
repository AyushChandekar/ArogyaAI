#!/bin/bash

# Healthcare Chatbot - Fixed Startup for Render
echo "🏥 Starting Healthcare Chatbot (Fixed for Render)..."

# Set environment variables
export PYTHONPATH=/app
export RASA_TELEMETRY_ENABLED=false
export PYTHONUNBUFFERED=1
export TF_CPP_MIN_LOG_LEVEL=3
export PYTHONDONTWRITEBYTECODE=1

cd /app

# Render ALWAYS sets PORT environment variable, but let's be explicit
if [ -n "$PORT" ]; then
    BIND_PORT=$PORT
    echo "🌐 Using Render's PORT: $BIND_PORT"
else
    BIND_PORT=10000
    echo "🌐 PORT not set, using default: $BIND_PORT"
fi

echo "🌐 Will bind to host 0.0.0.0 on port $BIND_PORT"

# Function to start fallback server
start_fallback() {
    echo "🔄 Starting fallback Flask server..."
    echo "🔄 Setting PORT=$BIND_PORT for Flask"
    export PORT=$BIND_PORT
    exec python3 simple_server.py
}

# Check if Flask is available (critical for fallback)
echo "🧪 Testing Flask availability..."
if python3 -c "import flask" 2>/dev/null; then
    echo "✅ Flask is available"
else
    echo "❌ Flask not available! Installing..."
    pip install flask flask-cors
fi

# Try training Rasa model first with ultra-minimal config
echo "📚 Attempting to train Rasa model (ultra-minimal)..."
if timeout 90 rasa train --config config-ultra-minimal.yml --domain domain.yml --data data --out models --quiet 2>/dev/null; then
    echo "✅ Ultra-minimal model training successful!"
elif timeout 60 rasa train --config config-minimal.yml --domain domain.yml --data data --out models --quiet 2>/dev/null; then
    echo "✅ Minimal model training successful!"
else
    echo "⚠️ Both training attempts failed or timed out"
    echo "🚀 Will try to start Rasa without trained model"
fi

# Try to start Rasa server
echo "🤖 Starting Rasa Server on port $BIND_PORT..."
echo "🔗 Server will be accessible at http://0.0.0.0:$BIND_PORT"

# Try Rasa with a shorter timeout to fail fast if there are issues
timeout 20 rasa run \
    -p $BIND_PORT \
    -i 0.0.0.0 \
    --enable-api \
    --cors "*" \
    --debug &

RASA_PID=$!

# Wait and check if Rasa started successfully
sleep 8
if kill -0 $RASA_PID 2>/dev/null; then
    echo "✅ Rasa server started successfully, PID: $RASA_PID"
    # Wait for Rasa process
    wait $RASA_PID
    echo "❌ Rasa process ended unexpectedly, falling back to Flask"
else
    echo "❌ Rasa server failed to start, switching to fallback"
fi

# If we get here, Rasa failed, so start fallback
echo "🔄 Rasa startup failed, switching to fallback server"
start_fallback