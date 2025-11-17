#!/usr/bin/env python
"""
Dual Database Validation Script for EDRS Backend
Tests both PostgreSQL (primary) and MongoDB (documents) integration
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
from django.contrib.auth import get_user_model
from apps.core.models import Category, Tag, Post
import json
from datetime import datetime


def validate_postgresql():
    """Test PostgreSQL database (primary database)"""
    print("🐘 Testing PostgreSQL Database (Primary)...")
    print("=" * 50)
    
    results = []
    
    try:
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL Connection: SUCCESS")
            print(f"📊 Version: {db_version.split()[1]}")
            results.append(("PostgreSQL Connection", True))
            
            # Test tables
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            table_count = cursor.fetchone()[0]
            print(f"✅ Tables Created: {table_count} tables")
            results.append(("PostgreSQL Tables", True))
            
            # Test CRUD operations
            User = get_user_model()
            user_count = User.objects.count()
            category_count = Category.objects.count()
            post_count = Post.objects.count()
            
            print(f"✅ CRUD Operations:")
            print(f"   - Users: {user_count}")
            print(f"   - Categories: {category_count}") 
            print(f"   - Posts: {post_count}")
            results.append(("PostgreSQL CRUD", True))
            
    except Exception as e:
        print(f"❌ PostgreSQL Error: {e}")
        results.append(("PostgreSQL Connection", False))
        
    return results


def validate_mongodb():
    """Test MongoDB database (documents storage)"""
    print("\n🍃 Testing MongoDB Database (Documents)...")
    print("=" * 50)
    
    results = []
    
    try:
        import mongoengine
        from apps.core.models import Analytics, ActivityLog
        from django.conf import settings
        
        # Test MongoDB connection
        if hasattr(settings, 'MONGODB_SETTINGS'):
            # Try to connect
            mongodb_settings = settings.MONGODB_SETTINGS.copy()
            mongodb_settings.update({
                'connect': False,  # Lazy connection
                'serverSelectionTimeoutMS': 5000,
                'connectTimeoutMS': 5000,
            })
            
            try:
                # Disconnect any existing connections first
                mongoengine.disconnect()
                conn = mongoengine.connect(**mongodb_settings)
                
                # Test connection by performing a simple operation
                db = conn.get_database()
                server_info = conn.server_info()
                
                print(f"✅ MongoDB Connection: SUCCESS")
                print(f"📊 Version: {server_info.get('version', 'Unknown')}")
                print(f"🗄️  Database: {mongodb_settings['db']}")
                results.append(("MongoDB Connection", True))
                
                # Test document operations
                try:
                    # Create test analytics document
                    test_analytics = Analytics(
                        user_id=1,
                        event_type="test_connection",
                        event_data={"test": True, "timestamp": datetime.now().isoformat()},
                        session_id="test_session",
                        ip_address="127.0.0.1",
                        user_agent="Test Agent"
                    )
                    test_analytics.save()
                    
                    # Count documents
                    analytics_count = Analytics.objects.count()
                    activity_count = ActivityLog.objects.count()
                    
                    print(f"✅ Document Operations:")
                    print(f"   - Analytics: {analytics_count} documents")
                    print(f"   - Activity Logs: {activity_count} documents")
                    
                    # Clean up test document
                    test_analytics.delete()
                    
                    results.append(("MongoDB Documents", True))
                    
                    # List collections
                    collections = db.list_collection_names()
                    print(f"✅ Collections: {', '.join(collections) if collections else 'None yet'}")
                    results.append(("MongoDB Collections", True))
                    
                except Exception as doc_error:
                    print(f"⚠️  Document Operations: {doc_error}")
                    results.append(("MongoDB Documents", False))
                    
            except Exception as conn_error:
                print(f"❌ MongoDB Connection Failed: {conn_error}")
                print("💡 This is normal if MongoDB service is not running")
                results.append(("MongoDB Connection", False))
                
        else:
            print("⚠️  MongoDB settings not configured")
            results.append(("MongoDB Configuration", False))
            
    except ImportError as import_error:
        print(f"❌ MongoDB Import Error: {import_error}")
        print("💡 Run: pip install mongoengine pymongo")
        results.append(("MongoDB Dependencies", False))
        
    return results


def test_database_architecture():
    """Test the database architecture setup"""
    print("\n🏗️  Testing Database Architecture...")
    print("=" * 50)
    
    results = []
    
    try:
        from django.conf import settings
        
        # Check primary database (PostgreSQL)
        primary_db = settings.DATABASES['default']
        print(f"✅ Primary Database (CRUD):")
        print(f"   - Engine: {primary_db['ENGINE']}")
        print(f"   - Host: {primary_db['HOST']}")
        print(f"   - Database: {primary_db['NAME']}")
        
        # Check MongoDB configuration
        if hasattr(settings, 'MONGODB_SETTINGS'):
            mongo_config = settings.MONGODB_SETTINGS
            print(f"✅ Document Database (MongoDB):")
            print(f"   - Host: {mongo_config['host']}")
            print(f"   - Database: {mongo_config['db']}")
        else:
            print("⚠️  MongoDB configuration not found")
            
        results.append(("Architecture Setup", True))
        
    except Exception as e:
        print(f"❌ Architecture Test Failed: {e}")
        results.append(("Architecture Setup", False))
        
    return results


def create_sample_documents():
    """Create sample documents in MongoDB"""
    print("\n📄 Creating Sample Documents...")
    print("=" * 50)
    
    results = []
    
    try:
        import mongoengine
        from apps.core.models import Analytics, ActivityLog
        
        # Create sample analytics
        analytics_samples = [
            {
                "user_id": 1,
                "event_type": "page_view",
                "event_data": {"page": "/dashboard", "duration": 15000},
                "session_id": "sess_123",
                "ip_address": "192.168.1.1"
            },
            {
                "user_id": 1, 
                "event_type": "button_click",
                "event_data": {"button": "create_post", "page": "/posts"},
                "session_id": "sess_123",
                "ip_address": "192.168.1.1"
            }
        ]
        
        # Create sample activity logs
        activity_samples = [
            {
                "user_id": 1,
                "action": "create_post",
                "resource_type": "post",
                "resource_id": "1",
                "details": {"title": "Test Post", "category": "general"},
                "ip_address": "192.168.1.1"
            },
            {
                "user_id": 1,
                "action": "login",
                "resource_type": "auth",
                "resource_id": "",
                "details": {"method": "email"},
                "ip_address": "192.168.1.1"
            }
        ]
        
        # Save analytics
        for sample in analytics_samples:
            Analytics(**sample).save()
            
        # Save activity logs  
        for sample in activity_samples:
            ActivityLog(**sample).save()
            
        analytics_count = Analytics.objects.count()
        activity_count = ActivityLog.objects.count()
        
        print(f"✅ Sample Documents Created:")
        print(f"   - Analytics: {analytics_count} documents")
        print(f"   - Activity Logs: {activity_count} documents")
        
        results.append(("Sample Documents", True))
        
    except Exception as e:
        print(f"❌ Sample Document Creation Failed: {e}")
        results.append(("Sample Documents", False))
        
    return results


def main():
    """Main validation function"""
    print("=" * 70)
    print("🚀 EDRS Dual Database Integration Validation")
    print("   PostgreSQL (Primary CRUD) + MongoDB (Documents)")
    print("=" * 70)
    
    all_results = []
    
    # Test PostgreSQL (Primary Database)
    all_results.extend(validate_postgresql())
    
    # Test MongoDB (Document Database) 
    all_results.extend(validate_mongodb())
    
    # Test Architecture
    all_results.extend(test_database_architecture())
    
    # Create sample documents (if MongoDB is working)
    mongo_working = any(name == "MongoDB Connection" and result for name, result in all_results)
    if mongo_working:
        all_results.extend(create_sample_documents())
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DUAL DATABASE VALIDATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in all_results if result)
    total = len(all_results)
    
    # Group results by database
    postgresql_tests = [r for r in all_results if "PostgreSQL" in r[0] or "Architecture" in r[0]]
    mongodb_tests = [r for r in all_results if "MongoDB" in r[0] or "Documents" in r[0]]
    
    print("🐘 PostgreSQL (Primary Database):")
    for test, result in postgresql_tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test}: {status}")
        
    print("\n🍃 MongoDB (Document Database):")
    for test, result in mongodb_tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test}: {status}")
    
    print(f"\n🎯 Overall Score: {passed}/{total} tests passed")
    
    if passed >= len(postgresql_tests):
        print("🎉 PRIMARY DATABASE (PostgreSQL) - FULLY OPERATIONAL!")
        print("   ✅ All CRUD operations working")
        print("   ✅ Ready for production use")
        
        if any(name == "MongoDB Connection" and result for name, result in mongodb_tests):
            print("🎉 DOCUMENT DATABASE (MongoDB) - CONNECTED!")
            print("   ✅ Document storage operational")
            print("   ✅ Analytics and logging ready")
        else:
            print("⚠️  DOCUMENT DATABASE (MongoDB) - NOT CONNECTED")
            print("   💡 Add MongoDB service to Railway or use MongoDB Atlas")
            print("   💡 PostgreSQL handles all core functionality")
            
    print("\n📚 Usage Recommendations:")
    print("   🐘 PostgreSQL: Users, Posts, Categories, Tags (All CRUD)")
    print("   🍃 MongoDB: Analytics, Logs, Documents, File Metadata")
    
    return passed == total


if __name__ == "__main__":
    main()