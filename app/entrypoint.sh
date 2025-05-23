#!/bin/bash
set -e

# Print environment information for debugging
echo "Starting application..."
echo "Current working directory: $(pwd)"
echo "Directory contents:"
ls -la
echo "PYTHONPATH: $PYTHONPATH"
echo "ROOT_PATH: $ROOT_PATH"

# Check if we're in the app directory or root
if [ -d "/app" ]; then
    echo "Found /app directory, using it as working directory"
    cd /app
    echo "New working directory: $(pwd)"
    echo "Directory contents:"
    ls -la
fi

if [ -d "/app/static" ]; then
    echo "Static directory exists at app/static"
else
    echo "WARNING: Static directory not found at app/static"
fi

# Apply migrations
echo "Applying migrations..."
exec python -m alembic upgrade head

# Start the application with increased logging
echo "Starting uvicorn server..."
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug
