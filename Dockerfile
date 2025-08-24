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

# Expose port 3000 (changed from 8000)
EXPOSE 3000

# Run the application on port 3000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
