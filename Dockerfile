# Simple Healthcare Chatbot Dockerfile for Render
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    netcat-traditional \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip 
RUN pip install --upgrade pip

# Install Rasa with minimal dependencies - force binary wheels
RUN pip install --only-binary=all --no-cache-dir rasa==3.5.10 rasa-sdk==3.5.1 requests>=2.28.0

# Copy all application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/logs

# Set environment variables for memory optimization
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV RASA_TELEMETRY_ENABLED=false
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=5005

# Expose port
EXPOSE 5005

# Make startup scripts executable
RUN chmod +x /app/start_production.sh /app/start_production_minimal.sh

# Use the memory-optimized startup script
CMD ["/app/start_production_minimal.sh"]
