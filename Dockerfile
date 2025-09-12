# Simple Healthcare Chatbot Dockerfile for Render
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip 
RUN pip install --upgrade pip

# Install Rasa with minimal dependencies - force binary wheels
RUN pip install --only-binary=all --no-cache-dir rasa==3.5.10 rasa-sdk==3.5.1 requests>=2.28.0

# Copy all application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV RASA_TELEMETRY_ENABLED=false

# Expose port
EXPOSE 5005

# Make startup script executable
RUN chmod +x /app/start_production.sh

# Use the startup script
CMD ["/app/start_production.sh"]