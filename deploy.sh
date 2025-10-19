# ============================================================================
# Deployment Script - deploy.sh
# ============================================================================


#!/bin/bash

# DevConnect Deployment Script
# Usage: ./deploy.sh

set -e

echo "================================================"
echo "DevConnect Deployment"
echo "================================================"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Pull latest code
echo "1. Pulling latest code..."
git pull origin main

# Install dependencies
echo "2. Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "3. Running database migrations..."
python manage.py migrate

# Collect static files
echo "4. Collecting static files..."
python manage.py collectstatic --noinput

# Update search vectors
echo "5. Updating search vectors..."
python manage.py update_search_vectors

# Restart services
echo "6. Restarting services..."
if [ "$USE_DOCKER" = "true" ]; then
    docker-compose restart web celery celery-beat
else
    sudo systemctl restart devconnect
    sudo systemctl restart devconnect-celery
    sudo systemctl restart devconnect-celery-beat
fi

echo "================================================"
echo "✓ Deployment complete!"
echo "================================================"
