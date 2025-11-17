#!/usr/bin/env python3
"""
AWS S3 Access Test for EDRS
Tests S3 bucket connectivity and access permissions
"""

import os
import sys
import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env.local if exists
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env.local')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value


class S3AccessTester:
    """Test AWS S3 access and functionality"""
    
    def __init__(self):
        self.results = []
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY') 
        self.bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
        self.region = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
        
        print("🔧 AWS S3 Access Test - EDRS")
        print("=" * 50)
    
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'status': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"    {details}")
    
    def test_credentials(self):
        """Test if AWS credentials are available"""
        try:
            if not self.aws_access_key or self.aws_access_key in ['your-access-key', 'local-mock-key']:
                self.log_test("AWS Credentials Check", False, 
                             "AWS_ACCESS_KEY_ID not configured or using placeholder")
                return False
            
            if not self.aws_secret_key or self.aws_secret_key in ['your-secret-key', 'local-mock-secret']:
                self.log_test("AWS Credentials Check", False,
                             "AWS_SECRET_ACCESS_KEY not configured or using placeholder")
                return False
            
            self.log_test("AWS Credentials Check", True, 
                         f"Access Key: {self.aws_access_key[:8]}***")
            return True
            
        except Exception as e:
            self.log_test("AWS Credentials Check", False, str(e))
            return False
    
    def test_bucket_configuration(self):
        """Test bucket configuration"""
        try:
            if not self.bucket_name or self.bucket_name in ['your-bucket-name', 'edrs-local-bucket']:
                self.log_test("S3 Bucket Configuration", False,
                             "AWS_STORAGE_BUCKET_NAME not configured or using placeholder")
                return False
            
            self.log_test("S3 Bucket Configuration", True,
                         f"Bucket: {self.bucket_name}, Region: {self.region}")
            return True
            
        except Exception as e:
            self.log_test("S3 Bucket Configuration", False, str(e))
            return False
    
    def test_s3_connection(self):
        """Test S3 service connection"""
        try:
            # Create S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region
            )
            
            # Test connection by listing buckets
            response = s3_client.list_buckets()
            bucket_names = [bucket['Name'] for bucket in response['Buckets']]
            
            self.log_test("S3 Service Connection", True,
                         f"Connected successfully. Available buckets: {len(bucket_names)}")
            return s3_client
            
        except NoCredentialsError:
            self.log_test("S3 Service Connection", False,
                         "No AWS credentials found")
            return None
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self.log_test("S3 Service Connection", False,
                         f"AWS Error: {error_code} - {e}")
            return None
        except Exception as e:
            self.log_test("S3 Service Connection", False,
                         f"Connection error: {str(e)}")
            return None
    
    def test_bucket_access(self, s3_client):
        """Test specific bucket access"""
        if not s3_client:
            return False
        
        try:
            # Check if bucket exists and is accessible
            response = s3_client.head_bucket(Bucket=self.bucket_name)
            
            self.log_test("Target Bucket Access", True,
                         f"Bucket '{self.bucket_name}' is accessible")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.log_test("Target Bucket Access", False,
                             f"Bucket '{self.bucket_name}' does not exist")
            elif error_code == '403':
                self.log_test("Target Bucket Access", False,
                             f"Access denied to bucket '{self.bucket_name}'")
            else:
                self.log_test("Target Bucket Access", False,
                             f"Error accessing bucket: {error_code}")
            return False
        except Exception as e:
            self.log_test("Target Bucket Access", False, str(e))
            return False
    
    def test_bucket_permissions(self, s3_client):
        """Test bucket permissions (list, read, write)"""
        if not s3_client:
            return False
        
        try:
            # Test LIST permission
            try:
                response = s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    MaxKeys=1
                )
                self.log_test("S3 List Permission", True,
                             f"Can list objects in bucket")
            except ClientError as e:
                self.log_test("S3 List Permission", False,
                             f"Cannot list objects: {e.response['Error']['Code']}")
            
            # Test WRITE permission with a test file
            test_key = f"edrs-test/access-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            test_content = f"EDRS S3 Access Test - {datetime.now().isoformat()}"
            
            try:
                s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=test_key,
                    Body=test_content.encode('utf-8'),
                    ContentType='text/plain'
                )
                self.log_test("S3 Write Permission", True,
                             f"Successfully uploaded test file: {test_key}")
                
                # Test READ permission
                try:
                    response = s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=test_key
                    )
                    content = response['Body'].read().decode('utf-8')
                    if content == test_content:
                        self.log_test("S3 Read Permission", True,
                                     f"Successfully read test file")
                    else:
                        self.log_test("S3 Read Permission", False,
                                     f"Content mismatch in read test")
                except ClientError as e:
                    self.log_test("S3 Read Permission", False,
                                 f"Cannot read object: {e.response['Error']['Code']}")
                
                # Clean up test file
                try:
                    s3_client.delete_object(
                        Bucket=self.bucket_name,
                        Key=test_key
                    )
                    self.log_test("S3 Delete Permission", True,
                                 f"Successfully deleted test file")
                except ClientError as e:
                    self.log_test("S3 Delete Permission", False,
                                 f"Cannot delete object: {e.response['Error']['Code']}")
                
            except ClientError as e:
                self.log_test("S3 Write Permission", False,
                             f"Cannot write object: {e.response['Error']['Code']}")
            
        except Exception as e:
            self.log_test("S3 Permissions Test", False, str(e))
            return False
    
    def test_bucket_structure(self, s3_client):
        """Test Rejlers folder structure in bucket"""
        if not s3_client:
            return False
        
        try:
            # Check for existing Rejlers structure
            response = s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='rejlers-abudhabi/',
                Delimiter='/',
                MaxKeys=10
            )
            
            if 'CommonPrefixes' in response:
                folders = [prefix['Prefix'] for prefix in response['CommonPrefixes']]
                self.log_test("Rejlers Folder Structure", True,
                             f"Found {len(folders)} folders in rejlers-abudhabi/")
                for folder in folders:
                    print(f"      📁 {folder}")
            else:
                self.log_test("Rejlers Folder Structure", True,
                             "No existing rejlers-abudhabi/ structure found (will be created on first upload)")
            
        except Exception as e:
            self.log_test("Rejlers Folder Structure", False, str(e))
    
    def run_all_tests(self):
        """Run complete S3 access test suite"""
        print(f"🕐 Starting S3 access tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test 1: Check credentials
        if not self.test_credentials():
            print("\n⚠️  Cannot proceed without valid AWS credentials")
            return self.generate_report()
        
        # Test 2: Check bucket configuration  
        if not self.test_bucket_configuration():
            print("\n⚠️  Cannot proceed without valid bucket configuration")
            return self.generate_report()
        
        # Test 3: Test S3 connection
        s3_client = self.test_s3_connection()
        
        # Test 4: Test bucket access
        if s3_client:
            self.test_bucket_access(s3_client)
            
            # Test 5: Test permissions
            self.test_bucket_permissions(s3_client)
            
            # Test 6: Test folder structure
            self.test_bucket_structure(s3_client)
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("📊 S3 ACCESS TEST SUMMARY")
        print("=" * 50)
        
        passed_tests = sum(1 for result in self.results if result['status'])
        total_tests = len(self.results)
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! AWS S3 is properly configured and accessible.")
        elif passed_tests > 0:
            print("\n⚠️  PARTIAL SUCCESS: Some S3 functionality is working.")
        else:
            print("\n❌ ALL TESTS FAILED: AWS S3 is not accessible.")
        
        # Configuration summary
        print(f"\n📋 Configuration Summary:")
        print(f"   AWS Access Key: {self.aws_access_key[:8] if self.aws_access_key else 'Not set'}***")
        print(f"   S3 Bucket: {self.bucket_name or 'Not set'}")
        print(f"   S3 Region: {self.region}")
        print(f"   USE_S3 Setting: {os.getenv('USE_S3', 'False')}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if not self.aws_access_key or self.aws_access_key in ['your-access-key', 'local-mock-key']:
            print("   • Set valid AWS_ACCESS_KEY_ID in .env.local")
        if not self.aws_secret_key or self.aws_secret_key in ['your-secret-key', 'local-mock-secret']:
            print("   • Set valid AWS_SECRET_ACCESS_KEY in .env.local")
        if not self.bucket_name or self.bucket_name in ['your-bucket-name', 'edrs-local-bucket']:
            print("   • Set valid AWS_STORAGE_BUCKET_NAME in .env.local")
        if os.getenv('USE_S3', 'False').lower() != 'true':
            print("   • Set USE_S3=True to enable S3 storage")
        
        return {
            'success': passed_tests == total_tests,
            'passed': passed_tests,
            'total': total_tests,
            'results': self.results
        }


def main():
    """Main function"""
    tester = S3AccessTester()
    report = tester.run_all_tests()
    
    # Save report to file
    report_file = os.path.join(os.path.dirname(__file__), f"s3_access_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return 0 if report['success'] else 1


if __name__ == "__main__":
    sys.exit(main())