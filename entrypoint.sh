#!/bin/bash
set -e

# Run Alembic Database Migrations
echo "Running Database Migrations..."
alembic upgrade head || { echo 'Migration failed'; exit 1; }

echo "Starting Application..."
# Execute the passed command (e.g., uvicorn) replacing the current shell 
# so it receives OS signals properly
exec "$@"
