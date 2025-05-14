FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app
COPY ./requirements.txt /app/

# Create necessary directories
RUN mkdir -p temp/uploads temp/reports

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Set environment variables
ENV ROOT_PATH=""
ENV PYTHONPATH="/"

# Use entrypoint script to initialize database and start application
ENTRYPOINT ["/app/entrypoint.sh"]
