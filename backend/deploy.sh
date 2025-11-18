#!/bin/bash

# EDRS Backend Production Deployment Script
# This script helps deploy the EDRS backend to production

set -e

echo "🚀 Starting EDRS Backend Production Deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.prod .env
    echo "📝 Please edit .env file with your production values and run this script again."
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=("SECRET_KEY" "POSTGRES_PASSWORD" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set in .env file"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser (if needed)
echo "👤 Creating superuser (if needed)..."
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Check service health
echo "🔍 Checking service health..."
sleep 5

if curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service health check failed"
    echo "📋 Service logs:"
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
fi

echo "🎉 EDRS Backend deployed successfully!"
echo ""
echo "📊 Service URLs:"
echo "   API: http://localhost:8000/api/"
echo "   Admin: http://localhost:8000/admin/"
echo "   Health: http://localhost:8000/api/health/"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "⚠️  Remember to:"
echo "   1. Configure your domain and SSL certificates"
echo "   2. Set up proper backup for PostgreSQL database"
echo "   3. Configure monitoring and alerting"
echo "   4. Review security settings in production"