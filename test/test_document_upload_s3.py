#!/usr/bin/env python3
"""
EDRS Document Upload and AWS S3 Test Script
Tests document upload functionality and S3 connectivity
"""
import os
import sys
import json
import requests
from pathlib import Path
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.local')
import django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from apps.pid_analysis.models import PIDProject, PIDDiagram
from core.storage import RejlersS3Storage

class DocumentUploadTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        self.user = None
        self.project = None
        
    def authenticate(self, email="tanzeem@rejlers.ae", password="rejlers2025"):
        """Login and get authentication token"""
        print("🔐 Testing Authentication...")
        
        login_data = {"email": email, "password": password}
        response = requests.post(
            f"{self.base_url}/api/auth/login/", 
            json=login_data
        )
        
        if response.status_code == 200:
            result = response.json()
            self.token = result.get('token')
            self.user = result.get('user')
            print(f"✅ Authentication successful for {self.user['email']}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
    
    def test_s3_connection(self):
        """Test AWS S3 connectivity and permissions"""
        print("\n🌐 Testing AWS S3 Connection...")
        
        # Check environment variables
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY') 
        aws_bucket = os.getenv('AWS_STORAGE_BUCKET_NAME', 'edrs-documents')
        aws_region = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
        
        print(f"📋 Configuration Check:")
        print(f"   AWS_ACCESS_KEY_ID: {'✅ Set' if aws_access_key else '❌ Not set'}")
        print(f"   AWS_SECRET_ACCESS_KEY: {'✅ Set' if aws_secret_key else '❌ Not set'}")
        print(f"   AWS_STORAGE_BUCKET_NAME: {aws_bucket}")
        print(f"   AWS_S3_REGION_NAME: {aws_region}")
        
        if not aws_access_key or not aws_secret_key:
            print("❌ AWS credentials not configured")
            print("💡 To configure AWS S3:")
            print("   1. Get credentials from Rejlers Abu Dhabi IT team")
            print("   2. Add to .env file:")
            print("      AWS_ACCESS_KEY_ID=your_key_here")
            print("      AWS_SECRET_ACCESS_KEY=your_secret_here")
            print("      AWS_STORAGE_BUCKET_NAME=rejlers-abudhabi-edrs")
            return False
            
        try:
            # Test S3 connection
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
            
            # Try to list buckets
            print("🔍 Testing S3 access...")
            response = s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            print(f"✅ S3 connection successful! Found {len(buckets)} buckets")
            
            # Check if our bucket exists
            if aws_bucket in buckets:
                print(f"✅ Target bucket '{aws_bucket}' exists")
                
                # Test bucket permissions
                try:
                    s3_client.head_object(Bucket=aws_bucket, Key='test/')
                    print("✅ Bucket read permissions verified")
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        print("✅ Bucket accessible (404 expected for non-existent key)")
                    else:
                        print(f"⚠️ Bucket access issue: {e}")
                
                # Test upload permissions
                try:
                    test_content = "EDRS Upload Test"
                    s3_client.put_object(
                        Bucket=aws_bucket,
                        Key='test/edrs_upload_test.txt',
                        Body=test_content.encode('utf-8'),
                        ContentType='text/plain'
                    )
                    print("✅ Bucket write permissions verified")
                    
                    # Clean up test file
                    s3_client.delete_object(Bucket=aws_bucket, Key='test/edrs_upload_test.txt')
                    print("✅ Test file cleanup completed")
                    
                except ClientError as e:
                    print(f"❌ Upload test failed: {e}")
                    return False
                    
            else:
                print(f"❌ Target bucket '{aws_bucket}' not found in accessible buckets")
                print(f"📋 Available buckets: {', '.join(buckets[:5])}")
                return False
                
            return True
            
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"❌ AWS credentials error: {e}")
            return False
        except ClientError as e:
            print(f"❌ AWS S3 connection failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def create_test_project(self):
        """Create a test project for document upload"""
        print("\n📁 Creating Test Project...")
        
        if not self.token:
            print("❌ Not authenticated")
            return False
            
        headers = {"Authorization": f"Token {self.token}"}
        
        project_data = {
            "name": "EDRS Upload Test Project",
            "description": "Test project for document upload functionality",
            "project_type": "oil_gas",
            "location": "Test Location",
            "client_company": "Test Client"
        }
        
        response = requests.post(
            f"{self.base_url}/api/pid-analysis/projects/",
            json=project_data,
            headers=headers
        )
        
        if response.status_code == 201:
            self.project = response.json()
            print(f"✅ Test project created: {self.project['name']} (ID: {self.project['id']})")
            return True
        else:
            print(f"❌ Project creation failed: {response.status_code} - {response.text}")
            return False
    
    def test_document_upload(self):
        """Test document upload functionality"""
        print("\n📄 Testing Document Upload...")
        
        if not self.project:
            print("❌ No test project available")
            return False
            
        # Create a test file
        test_file_content = b"Test P&ID diagram content"
        test_file_path = Path(project_root) / "test" / "test_upload.pdf"
        
        # Write test file
        test_file_path.write_bytes(test_file_content)
        print(f"📝 Created test file: {test_file_path}")
        
        try:
            headers = {"Authorization": f"Token {self.token}"}
            
            # Prepare upload data
            diagram_data = {
                "drawing_number": "TEST-001",
                "drawing_title": "Test Upload Document",
                "diagram_type": "process",
                "design_phase": "detailed",
                "revision": "A"
            }
            
            files = {
                'original_file': ('test_upload.pdf', open(test_file_path, 'rb'), 'application/pdf')
            }
            
            # Upload document
            response = requests.post(
                f"{self.base_url}/api/pid-analysis/projects/{self.project['id']}/diagrams/",
                data=diagram_data,
                files=files,
                headers=headers
            )
            
            files['original_file'][1].close()  # Close file handle
            
            if response.status_code == 201:
                diagram = response.json()
                print(f"✅ Document uploaded successfully!")
                print(f"   Diagram ID: {diagram['id']}")
                print(f"   File URL: {diagram.get('original_file', 'Not provided')}")
                print(f"   Status: {diagram.get('status', 'Unknown')}")
                
                # Test file access
                if diagram.get('original_file'):
                    file_url = diagram['original_file']
                    if file_url.startswith('http'):
                        # Test file download
                        file_response = requests.get(file_url, headers=headers)
                        if file_response.status_code == 200:
                            print("✅ Uploaded file accessible via URL")
                        else:
                            print(f"⚠️ File access issue: {file_response.status_code}")
                
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload test failed: {e}")
            return False
        finally:
            # Clean up test file
            if test_file_path.exists():
                test_file_path.unlink()
                print("🧹 Test file cleaned up")
    
    def test_storage_backend(self):
        """Test which storage backend is active"""
        print("\n💾 Testing Storage Backend...")
        
        print(f"📋 Storage Configuration:")
        print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
        print(f"   USE_S3: {getattr(settings, 'USE_S3', False)}")
        print(f"   MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'Not set')}")
        
        if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            print(f"   AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
        
        # Test custom storage class if available
        try:
            storage = RejlersS3Storage()
            print("✅ RejlersS3Storage class available")
            print(f"   Bucket: {storage.bucket_name}")
            print(f"   Region: {storage.region_name}")
        except Exception as e:
            print(f"❌ S3 Storage class error: {e}")
    
    def cleanup_test_data(self):
        """Clean up test project and data"""
        if self.project:
            print(f"\n🧹 Cleaning up test project...")
            headers = {"Authorization": f"Token {self.token}"}
            
            response = requests.delete(
                f"{self.base_url}/api/pid-analysis/projects/{self.project['id']}/",
                headers=headers
            )
            
            if response.status_code == 204:
                print("✅ Test project cleaned up")
            else:
                print(f"⚠️ Cleanup warning: {response.status_code}")
    
    def run_full_test(self):
        """Run complete test suite"""
        print("🚀 EDRS Document Upload & S3 Test Suite")
        print("=" * 50)
        
        # Test authentication
        if not self.authenticate():
            return False
            
        # Test storage backend
        self.test_storage_backend()
        
        # Test S3 connection
        s3_available = self.test_s3_connection()
        
        # Test document upload
        if self.create_test_project():
            upload_success = self.test_document_upload()
            self.cleanup_test_data()
        else:
            upload_success = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"🔐 Authentication: ✅ PASS")
        print(f"🌐 AWS S3 Connection: {'✅ PASS' if s3_available else '❌ FAIL (Credentials needed)'}")
        print(f"📄 Document Upload: {'✅ PASS' if upload_success else '❌ FAIL'}")
        
        if not s3_available:
            print("\n💡 To enable S3 storage:")
            print("   1. Contact Rejlers Abu Dhabi IT team for AWS credentials")
            print("   2. Add credentials to backend/.env.local file") 
            print("   3. Restart the backend server")
        
        if upload_success:
            print("\n🎉 Document upload is working!")
            if s3_available:
                print("   Files are stored in AWS S3 with proper organization")
            else:
                print("   Files are stored locally (development mode)")
        
        return upload_success and s3_available

if __name__ == "__main__":
    tester = DocumentUploadTest()
    tester.run_full_test()