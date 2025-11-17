from django.core.management.base import BaseCommand
from django.conf import settings
import mongoengine
from apps.core.models import Analytics, ActivityLog
from datetime import datetime


class Command(BaseCommand):
    help = 'Test MongoDB connection and document operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-samples',
            action='store_true',
            help='Create sample documents in MongoDB',
        )
        parser.add_argument(
            '--mongo-uri',
            type=str,
            help='MongoDB connection URI (overrides settings)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🍃 Testing MongoDB Integration...\n')
        )

        # Use custom URI if provided
        mongo_uri = options.get('mongo_uri')
        if mongo_uri:
            self.test_custom_mongodb(mongo_uri)
        else:
            self.test_configured_mongodb()
            
        if options['create_samples']:
            self.create_sample_documents()

    def test_configured_mongodb(self):
        """Test MongoDB with current settings"""
        try:
            if not hasattr(settings, 'MONGODB_SETTINGS'):
                self.stdout.write(
                    self.style.ERROR('❌ MongoDB settings not configured in settings.py')
                )
                return False

            mongodb_settings = settings.MONGODB_SETTINGS.copy()
            mongodb_settings.update({
                'connect': False,
                'serverSelectionTimeoutMS': 5000,
                'connectTimeoutMS': 5000,
            })

            self.stdout.write(f"🔍 Testing connection to: {mongodb_settings['host']}")
            
            # Disconnect existing connections
            mongoengine.disconnect()
            
            # Connect to MongoDB
            conn = mongoengine.connect(**mongodb_settings)
            
            # Test connection
            db = conn.get_database()
            server_info = conn.server_info()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ MongoDB Connection: SUCCESS')
            )
            self.stdout.write(f'   Version: {server_info.get("version", "Unknown")}')
            self.stdout.write(f'   Database: {mongodb_settings["db"]}')
            
            # List collections
            collections = db.list_collection_names()
            self.stdout.write(f'   Collections: {", ".join(collections) if collections else "None"}')
            
            # Test document operations
            self.test_document_operations()
            
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ MongoDB Connection Failed: {e}')
            )
            self.show_mongodb_setup_instructions()
            return False

    def test_custom_mongodb(self, mongo_uri):
        """Test MongoDB with custom URI"""
        try:
            self.stdout.write(f"🔍 Testing custom URI: {mongo_uri}")
            
            # Disconnect existing connections
            mongoengine.disconnect()
            
            # Connect with custom URI
            conn = mongoengine.connect(host=mongo_uri)
            
            # Test connection
            server_info = conn.server_info()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Custom MongoDB Connection: SUCCESS')
            )
            self.stdout.write(f'   Version: {server_info.get("version", "Unknown")}')
            
            # Test document operations
            self.test_document_operations()
            
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Custom MongoDB Connection Failed: {e}')
            )
            return False

    def test_document_operations(self):
        """Test document CRUD operations"""
        try:
            # Test Analytics document
            test_doc = Analytics(
                user_id=999,
                event_type="test_connection",
                event_data={"test": True, "timestamp": datetime.now().isoformat()},
                session_id="test_session",
                ip_address="127.0.0.1",
                user_agent="MongoDB Test"
            )
            test_doc.save()
            
            # Count documents
            analytics_count = Analytics.objects.count()
            activity_count = ActivityLog.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Document Operations: SUCCESS')
            )
            self.stdout.write(f'   Analytics Documents: {analytics_count}')
            self.stdout.write(f'   Activity Log Documents: {activity_count}')
            
            # Clean up test document
            test_doc.delete()
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Document Operations Failed: {e}')
            )

    def create_sample_documents(self):
        """Create sample analytics and activity log documents"""
        try:
            self.stdout.write(
                self.style.WARNING('\n🔧 Creating Sample Documents...\n')
            )
            
            # Sample analytics data
            analytics_samples = [
                Analytics(
                    user_id=1,
                    event_type="page_view",
                    event_data={"page": "/dashboard", "duration": 15000, "device": "desktop"},
                    session_id="sess_001",
                    ip_address="192.168.1.100",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                ),
                Analytics(
                    user_id=1,
                    event_type="button_click", 
                    event_data={"button": "create_post", "page": "/posts", "position": "header"},
                    session_id="sess_001",
                    ip_address="192.168.1.100",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                ),
                Analytics(
                    user_id=2,
                    event_type="search",
                    event_data={"query": "database integration", "results_count": 15},
                    session_id="sess_002", 
                    ip_address="192.168.1.101",
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                )
            ]
            
            # Sample activity logs
            activity_samples = [
                ActivityLog(
                    user_id=1,
                    action="create_post",
                    resource_type="post",
                    resource_id="1",
                    details={"title": "MongoDB Integration Guide", "category": "technical"},
                    ip_address="192.168.1.100"
                ),
                ActivityLog(
                    user_id=1,
                    action="update_profile",
                    resource_type="user",
                    resource_id="1",
                    details={"fields_updated": ["first_name", "bio"]},
                    ip_address="192.168.1.100"
                ),
                ActivityLog(
                    user_id=2,
                    action="login",
                    resource_type="auth",
                    resource_id="",
                    details={"method": "email", "success": True},
                    ip_address="192.168.1.101"
                )
            ]
            
            # Save analytics
            for analytics in analytics_samples:
                analytics.save()
                
            # Save activity logs
            for activity in activity_samples:
                activity.save()
                
            analytics_count = Analytics.objects.count()
            activity_count = ActivityLog.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Sample Documents Created:')
            )
            self.stdout.write(f'   Analytics: {analytics_count} documents')
            self.stdout.write(f'   Activity Logs: {activity_count} documents')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Sample Document Creation Failed: {e}')
            )

    def show_mongodb_setup_instructions(self):
        """Show MongoDB setup instructions"""
        self.stdout.write(
            self.style.WARNING('\n📚 MongoDB Setup Instructions:')
        )
        
        self.stdout.write('\n🚂 Option 1: Railway MongoDB Service')
        self.stdout.write('   1. Go to Railway Dashboard → Your Project')
        self.stdout.write('   2. Click "Add Service" → "Database" → "MongoDB"')
        self.stdout.write('   3. Copy the MongoDB connection string')
        self.stdout.write('   4. Update your .env file:')
        self.stdout.write('      MONGODB_URI=mongodb://mongo:password@mongodb.railway.internal:27017')
        
        self.stdout.write('\n☁️  Option 2: MongoDB Atlas (Cloud)')
        self.stdout.write('   1. Go to https://cloud.mongodb.com')
        self.stdout.write('   2. Create free cluster')
        self.stdout.write('   3. Get connection string')
        self.stdout.write('   4. Update your .env file:')
        self.stdout.write('      MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/edrs_mongo')
        
        self.stdout.write('\n🐳 Option 3: Local MongoDB')
        self.stdout.write('   1. Install MongoDB locally')
        self.stdout.write('   2. Start MongoDB service')
        self.stdout.write('   3. Use default connection:')
        self.stdout.write('      MONGODB_URI=mongodb://localhost:27017/edrs_mongo')
        
        self.stdout.write('\n🧪 Test Connection:')
        self.stdout.write('   python manage.py test_mongodb --mongo-uri "your_connection_string"')