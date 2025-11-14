#!/bin/bash

# Railway Deployment Entrypoint Script
# This script ensures proper startup sequence for Railway deployment

set -e  # Exit on any error

echo "🚀 Starting Railway deployment for EDRS Backend..."

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database connection..."
    
    python << EOF
import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

# Get DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not found")
    sys.exit(1)

# Parse URL
try:
    url = urlparse(database_url)
    
    # Wait for database connection
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=url.hostname,
                port=url.port,
                database=url.path[1:],
                user=url.username,
                password=url.password
            )
            conn.close()
            print("✅ Database connection successful!")
            break
        except Exception as e:
            if i == max_retries - 1:
                print(f"❌ Database connection failed after {max_retries} attempts: {e}")
                sys.exit(1)
            print(f"⏳ Attempt {i+1}/{max_retries}: Waiting for database...")
            time.sleep(2)
            
except Exception as e:
    print(f"❌ Database URL parsing failed: {e}")
    sys.exit(1)
EOF
}

# Function to run Django setup
setup_django() {
    echo "🔧 Setting up Django application..."
    
    # Create necessary directories
    mkdir -p staticfiles logs media
    
    # Run migrations
    echo "📦 Running database migrations..."
    python manage.py migrate --noinput
    
    # Collect static files
    echo "📂 Collecting static files..."
    python manage.py collectstatic --noinput --clear
    
    # Create superuser if needed (non-interactive)
    echo "👤 Ensuring admin user exists..."
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Create admin user if not exists
if not User.objects.filter(is_superuser=True).exists():
    try:
        User.objects.create_superuser(
            username='admin',
            email='admin@edrs.com', 
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print('✅ Admin user created: admin/admin123')
    except Exception as e:
        print(f'⚠️  Admin user creation skipped: {e}')
else:
    print('ℹ️  Admin user already exists')
" || true
}

# Function to validate setup
validate_setup() {
    echo "🔍 Validating application setup..."
    
    python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model

try:
    # Test database
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    
    # Test models
    User = get_user_model()
    user_count = User.objects.count()
    
    print(f'✅ Database validation successful')
    print(f'✅ Users in database: {user_count}')
    
except Exception as e:
    print(f'❌ Validation failed: {e}')
    exit(1)
" || {
    echo "❌ Application validation failed"
    exit 1
}
}

# Main execution
main() {
    echo "🏁 Starting Railway deployment process..."
    
    # Wait for database
    wait_for_db
    
    # Setup Django
    setup_django
    
    # Validate setup
    validate_setup
    
    echo "✅ Deployment setup completed successfully!"
    echo "🚀 Starting Gunicorn server..."
    
    # Start Gunicorn with Railway-optimized settings
    exec gunicorn \
        --bind 0.0.0.0:${PORT:-8000} \
        --workers ${WEB_CONCURRENCY:-2} \
        --timeout ${GUNICORN_TIMEOUT:-120} \
        --keep-alive ${GUNICORN_KEEP_ALIVE:-5} \
        --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
        --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-100} \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --preload \
        core.wsgi:application
}

# Handle signals gracefully
trap 'echo "🛑 Received shutdown signal"; exit 0' SIGTERM SIGINT

# Run main function
main "$@"