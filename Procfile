release: cd backend && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: cd backend && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT