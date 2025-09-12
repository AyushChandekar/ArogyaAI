# Healthcare Chatbot Dockerfile for Render Deployment
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV RASA_X_PASSWORD=admin
ENV PYTHONUNBUFFERED=1

# Expose ports for Rasa server (5005) and Action server (5055)
EXPOSE 5005 5055

# Make startup script executable
RUN chmod +x /app/start_production.sh

# Use the startup script
CMD ["/app/start_production.sh"]
