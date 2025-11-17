#!/usr/bin/env python
"""
Database Validation Script for EDRS Backend
This script validates the PostgreSQL database connection and checks database integration
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from apps.core.models import Category, Tag, Post
import psycopg2
from urllib.parse import urlparse


def validate_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing Database Connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            print(f"✅ Database Connection: SUCCESS")
            print(f"📊 PostgreSQL Version: {db_version}")
            return True
    except Exception as e:
        print(f"❌ Database Connection: FAILED")
        print(f"Error: {e}")
        return False


def validate_database_url():
    """Validate DATABASE_URL configuration"""
    print("\n🔍 Validating DATABASE_URL Configuration...")
    
    from django.conf import settings
    db_config = settings.DATABASES['default']
    
    print(f"✅ Database Engine: {db_config['ENGINE']}")
    print(f"✅ Database Name: {db_config['NAME']}")
    print(f"✅ Database Host: {db_config['HOST']}")
    print(f"✅ Database Port: {db_config['PORT']}")
    print(f"✅ Database User: {db_config['USER']}")
    
    # Check if using Railway DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if database_url and 'railway' in database_url:
        print("🚂 Railway PostgreSQL detected!")
        parsed = urlparse(database_url)
        print(f"   Host: {parsed.hostname}")
        print(f"   Port: {parsed.port}")
        print(f"   Database: {parsed.path[1:]}")
    
    return True


def validate_migrations():
    """Check if migrations are applied"""
    print("\n🔍 Checking Database Migrations...")
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print(f"⚠️  Pending Migrations: {len(plan)} migrations need to be applied")
            for migration, backwards in plan:
                print(f"   - {migration}")
            return False
        else:
            print("✅ All Migrations Applied: Database is up to date")
            return True
    except Exception as e:
        print(f"❌ Migration Check Failed: {e}")
        return False


def validate_models():
    """Test model operations"""
    print("\n🔍 Testing Model Operations...")
    
    try:
        # Test User model
        User = get_user_model()
        user_count = User.objects.count()
        print(f"✅ User Model: {user_count} users in database")
        
        # Test Category model
        category_count = Category.objects.count()
        print(f"✅ Category Model: {category_count} categories in database")
        
        # Test Tag model
        tag_count = Tag.objects.count()
        print(f"✅ Tag Model: {tag_count} tags in database")
        
        # Test Post model
        post_count = Post.objects.count()
        print(f"✅ Post Model: {post_count} posts in database")
        
        return True
    except Exception as e:
        print(f"❌ Model Operations Failed: {e}")
        return False


def check_database_tables():
    """List all database tables"""
    print("\n🔍 Checking Database Tables...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                    count = cursor.fetchone()[0]
                    print(f"   - {table[0]}: {count} records")
            else:
                print("⚠️  No tables found. Run migrations first.")
            
            return len(tables) > 0
    except Exception as e:
        print(f"❌ Table Check Failed: {e}")
        return False


def test_crud_operations():
    """Test Create, Read, Update, Delete operations"""
    print("\n🔍 Testing CRUD Operations...")
    
    try:
        # Create a test category
        test_category = Category.objects.create(
            name="Test Category",
            description="This is a test category for validation",
            slug="test-category"
        )
        print("✅ CREATE: Test category created successfully")
        
        # Read the category
        retrieved_category = Category.objects.get(slug="test-category")
        print("✅ READ: Test category retrieved successfully")
        
        # Update the category
        retrieved_category.description = "Updated test description"
        retrieved_category.save()
        print("✅ UPDATE: Test category updated successfully")
        
        # Delete the category
        retrieved_category.delete()
        print("✅ DELETE: Test category deleted successfully")
        
        return True
    except Exception as e:
        print(f"❌ CRUD Operations Failed: {e}")
        return False


def generate_test_data():
    """Generate some test data for validation"""
    print("\n🔍 Generating Test Data...")
    
    try:
        # Create test user if not exists
        User = get_user_model()
        if not User.objects.filter(username='testuser').exists():
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpassword123'
            )
            print("✅ Test user created: testuser")
        else:
            user = User.objects.get(username='testuser')
            print("✅ Test user already exists: testuser")
        
        # Create test category if not exists
        if not Category.objects.filter(slug='general').exists():
            category = Category.objects.create(
                name="General",
                description="General category for posts",
                slug="general"
            )
            print("✅ Test category created: General")
        else:
            category = Category.objects.get(slug='general')
            print("✅ Test category already exists: General")
        
        # Create test tag if not exists
        if not Tag.objects.filter(name='test').exists():
            tag = Tag.objects.create(
                name="test",
                color="#007bff"
            )
            print("✅ Test tag created: test")
        else:
            tag = Tag.objects.get(name='test')
            print("✅ Test tag already exists: test")
        
        return True
    except Exception as e:
        print(f"❌ Test Data Generation Failed: {e}")
        return False


def main():
    """Main validation function"""
    print("=" * 60)
    print("🚀 EDRS Database Integration Validation")
    print("=" * 60)
    
    results = {
        'connection': validate_database_connection(),
        'config': validate_database_url(),
        'migrations': validate_migrations(),
        'tables': check_database_tables(),
        'models': validate_models(),
        'crud': test_crud_operations(),
        'test_data': generate_test_data()
    }
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test.upper().replace('_', ' ')}: {status}")
    
    print(f"\n🎯 Overall Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Database integration is working perfectly!")
        print("\n📝 Next Steps:")
        print("   1. Your backend is fully connected to Railway PostgreSQL")
        print("   2. You can start using the API endpoints")
        print("   3. Frontend can connect to: https://your-domain.railway.app/api/")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        if not results['migrations']:
            print("💡 Tip: Run 'python manage.py migrate' to apply pending migrations")
    
    return passed == total


if __name__ == "__main__":
    main()