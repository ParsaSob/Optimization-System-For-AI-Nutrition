# Meal Optimization API Dockerfile
# Force clean build for Railway deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Set environment variable for port
ENV PORT=8000

# Expose port
EXPOSE 8000

# Start command with shell expansion
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port \${PORT:-8000}"
