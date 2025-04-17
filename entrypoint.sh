#!/bin/bash
set -e

echo "Waiting for 2 seconds before starting database operations..."
sleep 2

cd /app/backend

echo "Setting up the database..."
echo "Environment: $FLASK_ENV"
echo "Database URL: $DATABASE_URL"

echo "Running database migrations..."
flask db upgrade

# Check if we need to seed the database
if [ "$SEED_DB" = "true" ]; then
    echo "Seeding the database..."
    flask seed-db
fi

echo "Database setup complete!"

# Start the application
if [ "$FLASK_ENV" = "development" ]; then
    echo "Starting Flask development server..."
    exec flask run --host 0.0.0.0 --reload
else
    echo "Starting Gunicorn production server..."
    cd /app/backend/src
    exec gunicorn --bind 0.0.0.0:5000 wsgi:app
fi 