FROM python:3.12-slim

WORKDIR /root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

# Install yarn first
RUN npm install -g yarn

# Copy requirements file
COPY pyproject.toml .
COPY poetry.lock .

# Install Python dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY ./app /root/app/
# COPY ./config /app/config

# Install app
WORKDIR /root
RUN poetry install

# Build frontend
WORKDIR /root/app/frontend

# Use yarn instead of npm
RUN yarn install && yarn build

# Create necessary directories
RUN mkdir -p /root/app/temp/uploads /root/app/temp/reports

# Make entrypoint script executable
RUN chmod +x /root/app/entrypoint.sh

# Expose port
EXPOSE 8000

# Set environment variables
ENV ROOT_PATH=""
ENV PYTHONPATH="/root/app"
ENV LOG_LEVEL="DEBUG"
ENV ENVIRONMENT="production"
ENV CONFIG_PATH="/root/app/config/.env"

# Use entrypoint script to initialize database and start application
ENTRYPOINT ["/root/app/entrypoint.sh"]
