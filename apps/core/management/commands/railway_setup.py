"""
Railway Deployment Management Command
Handles the complete setup process for Railway deployment
"""

from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth import get_user_model
import os
import sys

class Command(BaseCommand):
    help = 'Prepare Django application for Railway deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running migrations',
        )
        parser.add_argument(
            '--skip-static',
            action='store_true', 
            help='Skip collecting static files',
        )
        parser.add_argument(
            '--skip-admin',
            action='store_true',
            help='Skip creating admin user',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting Railway deployment setup...')
        
        # Test database connection first
        if not self.test_database():
            return
            
        # Run migrations
        if not options['skip_migrations']:
            self.run_migrations()
            
        # Collect static files
        if not options['skip_static']:
            self.collect_static()
            
        # Create admin user
        if not options['skip_admin']:
            self.create_admin_user()
            
        self.stdout.write(
            self.style.SUCCESS('✅ Railway deployment setup completed successfully!')
        )

    def test_database(self):
        """Test database connectivity"""
        self.stdout.write('🔍 Testing database connection...')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            if result and result[0] == 1:
                self.stdout.write(self.style.SUCCESS('✅ Database connection successful'))
                return True
            else:
                self.stdout.write(self.style.ERROR('❌ Database connection failed - unexpected result'))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database connection failed: {e}'))
            
            # Check if it's a Railway internal network issue
            db_url = os.environ.get('DATABASE_URL', '')
            if 'postgres.railway.internal' in db_url:
                self.stdout.write(self.style.WARNING(
                    '⚠️  Detected Railway internal network URL. This suggests Docker mode is being used.'
                ))
                self.stdout.write(self.style.WARNING(
                    '💡 Solution: Configure Railway to use NIXPACKS buildpack instead of Docker'
                ))
            
            return False

    def run_migrations(self):
        """Run Django migrations"""
        self.stdout.write('📦 Running database migrations...')
        
        try:
            # Use call_command instead of execute_from_command_line for better control
            from django.core.management import call_command
            call_command('migrate', '--noinput', verbosity=1)
            self.stdout.write(self.style.SUCCESS('✅ Migrations completed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Migration failed: {e}'))
            sys.exit(1)

    def collect_static(self):
        """Collect static files"""
        self.stdout.write('📂 Collecting static files...')
        
        try:
            from django.core.management import call_command
            call_command('collectstatic', '--noinput', '--clear', verbosity=1)
            self.stdout.write(self.style.SUCCESS('✅ Static files collected'))
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Static files collection warning: {e}'))
            # Don't exit on static files issues

    def create_admin_user(self):
        """Create admin user if it doesn't exist"""
        self.stdout.write('👤 Ensuring admin user exists...')
        
        try:
            User = get_user_model()
            
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@edrs.com',
                    password='admin123',  # Change this in production
                    first_name='Admin',
                    last_name='User'
                )
                self.stdout.write(self.style.SUCCESS('✅ Admin user created: admin/admin123'))
            else:
                admin_count = User.objects.filter(is_superuser=True).count()
                self.stdout.write(self.style.SUCCESS(f'ℹ️  {admin_count} admin user(s) already exist'))
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Admin user creation skipped: {e}'))