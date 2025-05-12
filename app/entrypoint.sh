#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
  if pg_isready -h $DB_HOST -U $DB_USER -d $DB_NAME; then
    echo "PostgreSQL is ready!"
    break
  fi
  echo "Waiting for PostgreSQL to be ready... ($i/30)"
  sleep 2
done

# Initialize the database without dropping tables in production
echo "Initializing database..."
python -m app.database.init_db

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
