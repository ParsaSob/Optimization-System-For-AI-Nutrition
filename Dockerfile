FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Make start.sh executable
RUN chmod +x start.sh

# Expose port (will be set by Railway)
EXPOSE $PORT

# Use start.sh script to handle PORT expansion
CMD ["./start.sh"]
