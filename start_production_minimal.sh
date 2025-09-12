#!/bin/bash

# Healthcare Chatbot - Memory Optimized Production Startup
echo "🏥 Starting Healthcare Chatbot (Memory Optimized)..."

# Set environment variables
export PYTHONPATH=/app
export RASA_TELEMETRY_ENABLED=false
export PYTHONUNBUFFERED=1

# Optimize for low memory
export TF_CPP_MIN_LOG_LEVEL=2
export PYTHONDONTWRITEBYTECODE=1

# Kill any existing processes (handle missing pkill gracefully)
if command -v pkill &> /dev/null; then
    pkill -f "rasa run" || true
    pkill -f "rasa run actions" || true
else
    echo "⚠️ pkill not available, using alternative cleanup"
    ps aux | grep "rasa run" | grep -v grep | awk '{print $2}' | xargs -r kill -9 || true
fi

sleep 2

# Check if we need to train a model
if [ ! -d "/app/models" ] || [ -z "$(ls -A /app/models)" ]; then
    echo "📚 Training minimal Rasa model (memory constrained)..."
    cd /app
    
    # Set memory optimization flags
    export TF_CPP_MIN_LOG_LEVEL=3
    export CUDA_VISIBLE_DEVICES=""
    
    # Train using RASA CLI with minimal config
    echo "Using config: config-minimal.yml"
    rasa train --config config-minimal.yml --domain domain.yml --data data --out models --fixed-model-name healthcare-model --quiet || {
        echo "⚠️ Minimal training failed, trying with standard config..."
        rasa train --config config.yml --domain domain.yml --data data --out models --fixed-model-name healthcare-model --quiet || {
            echo "❌ All training attempts failed"
            echo "📋 Checking training data..."
            ls -la data/ || echo "No data directory found"
            ls -la . | grep -E "\.(yml|yaml)$" || echo "No YAML files found"
            exit 1
        }
    }
    echo "✅ Model training completed"
else
    echo "✅ Using existing trained model"
fi

# Start only Rasa server (no separate action server to save memory)
echo "🤖 Starting Rasa Server on port 5005..."
cd /app

# Use exec to replace the shell process and save memory
exec rasa run \
    --port 5005 \
    --host 0.0.0.0 \
    --enable-api \
    --cors "*" \
    --auth-token "${RASA_AUTH_TOKEN:-}" \
    --endpoints endpoints.yml \
    --debug