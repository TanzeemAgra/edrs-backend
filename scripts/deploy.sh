#!/bin/bash

# Railway deployment script for Django backend
echo "🚀 Starting Railway deployment..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import os
import time
import psycopg2
from urllib.parse import urlparse

# Parse DATABASE_URL
db_url = os.environ.get('DATABASE_URL', '')
if db_url:
    url = urlparse(db_url)
    for i in range(30):  # Try for 30 seconds
        try:
            conn = psycopg2.connect(
                host=url.hostname,
                port=url.port,
                database=url.path[1:],
                user=url.username,
                password=url.password
            )
            conn.close()
            print('Database connection successful!')
            break
        except Exception as e:
            if i == 29:
                print(f'Database connection failed: {e}')
            time.sleep(1)
"

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
echo "👤 Creating superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
try:
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print('Superuser created successfully!')
    else:
        print('Superuser already exists.')
except Exception as e:
    print(f'Superuser creation failed: {e}')
"

echo "✅ Deployment setup completed!"
echo "🌐 Health check available at: /health/"