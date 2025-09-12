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
    
    # Train with minimal memory usage
    python -c "
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings('ignore')
from rasa import train
train.train(
    domain='domain.yml',
    config='config-minimal.yml',
    training_files=['data/'],
    output='models/',
    fixed_model_name='healthcare-model'
)
print('✅ Model training completed')
" 2>/dev/null || {
    echo "❌ Model training failed, using fallback"
    exit 1
}
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