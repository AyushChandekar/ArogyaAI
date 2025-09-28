# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models data

# Set environment variables
ENV PYTHONPATH=/app
ENV RASA_SERVER_URL=http://localhost:5005/webhooks/rest/webhook

# Expose ports
EXPOSE 8000 5001 5005 5055

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🏥 Starting ArogyaAI Services..."\n\
\n\
# Start Rasa server in background\n\
echo "🤖 Starting Rasa server..."\n\
rasa run --enable-api --cors="*" --port 5005 &\n\
RASA_PID=$!\n\
\n\
# Wait for Rasa to start\n\
sleep 10\n\
\n\
# Start Rasa actions server in background\n\
echo "⚡ Starting Rasa actions server..."\n\
rasa run actions --port 5055 &\n\
ACTIONS_PID=$!\n\
\n\
# Wait for actions server to start\n\
sleep 5\n\
\n\
# Start the main application\n\
echo "🚀 Starting FastAPI backend..."\n\
python backend.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["/app/start.sh"]