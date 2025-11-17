from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth import get_user_model
from apps.core.models import Category, Tag, Post
import json


class Command(BaseCommand):
    help = 'Test database integration and connectivity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data in the database',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Testing Database Integration...\n')
        )

        # Test 1: Database Connection
        self.test_database_connection()
        
        # Test 2: Check Migrations
        self.check_migrations()
        
        # Test 3: Test Models
        self.test_models()
        
        # Test 4: Check Tables
        self.check_tables()
        
        # Test 5: Create test data if requested
        if options['create_test_data']:
            self.create_test_data()

    def test_database_connection(self):
        """Test database connectivity"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()[0]
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Database Connection: SUCCESS')
                )
                self.stdout.write(f'   PostgreSQL Version: {db_version}\n')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Database Connection: FAILED - {e}\n')
            )

    def check_migrations(self):
        """Check migration status"""
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Pending Migrations: {len(plan)} migrations need to be applied')
                )
                for migration, backwards in plan:
                    self.stdout.write(f'   - {migration}')
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ All Migrations Applied: Database is up to date')
                )
            self.stdout.write('')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Migration Check Failed: {e}\n')
            )

    def test_models(self):
        """Test model operations"""
        try:
            User = get_user_model()
            
            # Count records in each model
            user_count = User.objects.count()
            category_count = Category.objects.count()
            tag_count = Tag.objects.count()
            post_count = Post.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Model Operations: SUCCESS')
            )
            self.stdout.write(f'   Users: {user_count}')
            self.stdout.write(f'   Categories: {category_count}')
            self.stdout.write(f'   Tags: {tag_count}')
            self.stdout.write(f'   Posts: {post_count}\n')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Model Operations Failed: {e}\n')
            )

    def check_tables(self):
        """List database tables"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Database Tables: {len(tables)} tables found')
                )
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                    count = cursor.fetchone()[0]
                    self.stdout.write(f'   - {table[0]}: {count} records')
                
                self.stdout.write('')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Table Check Failed: {e}\n')
            )

    def create_test_data(self):
        """Create test data for validation"""
        self.stdout.write(
            self.style.WARNING('🔧 Creating Test Data...\n')
        )
        
        try:
            User = get_user_model()
            
            # Create test user
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
            )
            if created:
                user.set_password('testpassword123')
                user.save()
                self.stdout.write('✅ Test user created: testuser')
            else:
                self.stdout.write('ℹ️  Test user already exists: testuser')
            
            # Create test category
            category, created = Category.objects.get_or_create(
                slug='general',
                defaults={
                    'name': 'General',
                    'description': 'General category for posts'
                }
            )
            if created:
                self.stdout.write('✅ Test category created: General')
            else:
                self.stdout.write('ℹ️  Test category already exists: General')
            
            # Create test tag
            tag, created = Tag.objects.get_or_create(
                name='test',
                defaults={'color': '#007bff'}
            )
            if created:
                self.stdout.write('✅ Test tag created: test')
            else:
                self.stdout.write('ℹ️  Test tag already exists: test')
            
            # Create test post
            post, created = Post.objects.get_or_create(
                slug='test-post',
                defaults={
                    'title': 'Test Post',
                    'content': 'This is a test post to validate database integration.',
                    'excerpt': 'Test post for validation',
                    'author': user,
                    'category': category,
                    'status': 'published'
                }
            )
            if created:
                post.tags.add(tag)
                self.stdout.write('✅ Test post created: Test Post')
            else:
                self.stdout.write('ℹ️  Test post already exists: Test Post')
            
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Test data creation completed!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Test Data Creation Failed: {e}')
            )