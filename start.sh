#!/bin/bash
# start.sh - Startup script for Django app on Fly.io

# Exit on error
set -e

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Start the application
gunicorn eiken_project.wsgi:application --bind 0.0.0.0:8000 --workers 2 