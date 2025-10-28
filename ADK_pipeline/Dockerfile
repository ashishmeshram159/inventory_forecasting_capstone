# ----------------------------------------
# Base image
# ----------------------------------------
FROM python:3.13.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into container
COPY . .

# Make sure Python can find your packages (fixes Pylance & runtime import errors)
ENV PYTHONPATH=/app/ADK_pipeline:$PYTHONPATH

# Environment variables
ENV APP_NAME=inventory_conversation_system \
    PORT=8080 \
    PYTHONUNBUFFERED=1

# Expose the app port
EXPOSE 8080

# Default command (update if main.py path differs)
CMD ["python", "ADK_pipeline/main.py"]
