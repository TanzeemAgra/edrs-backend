#!/bin/bash
# Railway startup script for EDRS backend
set -e

echo "🚀 Starting EDRS Backend..."

# Run migrations in background to avoid blocking startup
echo "🔄 Running migrations..."
python3 manage.py migrate --noinput &
MIGRATE_PID=$!

# Collect static files
echo "📋 Collecting static files..."
python3 manage.py collectstatic --noinput --clear || echo "⚠️ Static files collection failed"

# Wait for migrations to complete (with timeout)
echo "⏳ Waiting for migrations to complete..."
timeout 60 wait $MIGRATE_PID || echo "⚠️ Migrations timed out, continuing anyway..."

echo "✅ Startup complete, launching Gunicorn..."

# Start Gunicorn
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --timeout 30 \
    --max-requests 1000 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info