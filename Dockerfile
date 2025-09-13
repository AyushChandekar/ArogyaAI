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
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip 
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt .

# Install all dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

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
ENV PORT=10000

# Expose port
EXPOSE 10000

# Make startup scripts executable
RUN chmod +x /app/start_production*.sh

# Use the fixed startup script
CMD ["/app/start_production_fixed.sh"]
