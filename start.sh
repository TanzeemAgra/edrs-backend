#!/bin/bash

# Railway Deployment Start Script for EDRS Django Backend
set -e  # Exit on any error

echo "🚀 Starting EDRS Django Backend Deployment..."
echo "======================================"

# Environment Detection
echo "📋 Environment Information:"
echo "Python Version: $(python --version)"
echo "Current Directory: $(pwd)"
echo "Environment: ${RAILWAY_ENVIRONMENT:-development}"

# Django Setup
echo ""
echo "⚙️  Django Configuration:"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-core.settings}"

# Database Migration
echo ""
echo "🗃️  Running Database Migrations..."
python manage.py collectstatic --noinput --verbosity 2
python manage.py migrate --noinput

# Create Superuser (if needed)
if [ "${CREATE_SUPERUSER:-false}" = "true" ]; then
    echo ""
    echo "👤 Creating Django Superuser..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@edrs.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('ℹ️  Superuser already exists')
EOF
fi

# Health Check
echo ""
echo "🔍 Django Health Check..."
python manage.py check --deploy

# Start Application
echo ""
echo "🌐 Starting Django Server..."
echo "Port: ${PORT:-8000}"
echo "Host: 0.0.0.0"
echo "======================================"

# Use Gunicorn for production, Django dev server for development
if [ "${RAILWAY_ENVIRONMENT}" = "production" ]; then
    echo "🚀 Starting with Gunicorn (Production Mode)..."
    exec gunicorn core.wsgi:application \
        --bind 0.0.0.0:${PORT:-8000} \
        --workers ${WEB_CONCURRENCY:-3} \
        --worker-class gthread \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 30 \
        --keep-alive 5 \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        --capture-output
else
    echo "🛠️  Starting with Django Dev Server (Development Mode)..."
    exec python manage.py runserver 0.0.0.0:${PORT:-8000}
fi