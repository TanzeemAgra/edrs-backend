#!/usr/bin/env python3
"""
AWS S3 Bucket Access Test for rejlers-edrs-project
Tests connectivity, permissions, and operations on the specified S3 bucket
ARN: arn:aws:s3:::rejlers-edrs-project
"""

import os
import sys
import json
from datetime import datetime
from io import BytesIO

# Add Django project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.local')

try:
    import django
    django.setup()
except Exception as e:
    print(f"⚠️  Django setup failed: {e}")

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError as e:
    print(f"❌ boto3 not available: {e}")
    BOTO3_AVAILABLE = False

class S3BucketTester:
    """Test AWS S3 bucket access and operations"""
    
    def __init__(self, bucket_name="rejlers-edrs-project", region_name="us-east-1"):
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.bucket_arn = f"arn:aws:s3:::{bucket_name}"
        self.s3_client = None
        self.s3_resource = None
        
        # Test results
        self.test_results = {
            'bucket_name': bucket_name,
            'bucket_arn': self.bucket_arn,
            'region': region_name,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
    
    def print_header(self):
        """Print test header"""
        print("=" * 80)
        print("🔍 AWS S3 BUCKET ACCESS TEST")
        print("=" * 80)
        print(f"Bucket Name: {self.bucket_name}")
        print(f"Bucket ARN:  {self.bucket_arn}")
        print(f"Region:      {self.region_name}")
        print(f"Test Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def test_boto3_availability(self):
        """Test if boto3 is available"""
        print("\n📦 Testing boto3 availability...")
        
        if not BOTO3_AVAILABLE:
            self.test_results['tests']['boto3_available'] = {
                'success': False,
                'error': 'boto3 not installed or importable'
            }
            print("❌ boto3 is not available")
            return False
        
        try:
            import boto3
            print(f"✅ boto3 version: {boto3.__version__}")
            self.test_results['tests']['boto3_available'] = {
                'success': True,
                'version': boto3.__version__
            }
            return True
        except Exception as e:
            print(f"❌ boto3 error: {e}")
            self.test_results['tests']['boto3_available'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def test_credentials(self):
        """Test AWS credentials"""
        print("\n🔐 Testing AWS credentials...")
        
        try:
            # Try to create S3 client
            self.s3_client = boto3.client('s3', region_name=self.region_name)
            self.s3_resource = boto3.resource('s3', region_name=self.region_name)
            
            # Test credentials by listing buckets
            response = self.s3_client.list_buckets()
            
            print("✅ AWS credentials are valid")
            print(f"✅ Found {len(response.get('Buckets', []))} accessible buckets")
            
            # Check if our target bucket is in the list
            bucket_names = [bucket['Name'] for bucket in response.get('Buckets', [])]
            if self.bucket_name in bucket_names:
                print(f"✅ Target bucket '{self.bucket_name}' found in accessible buckets")
                bucket_accessible = True
            else:
                print(f"⚠️  Target bucket '{self.bucket_name}' not found in accessible buckets")
                bucket_accessible = False
            
            self.test_results['tests']['credentials'] = {
                'success': True,
                'total_buckets': len(response.get('Buckets', [])),
                'target_bucket_accessible': bucket_accessible,
                'accessible_buckets': bucket_names[:5]  # First 5 for privacy
            }
            
            return True
            
        except NoCredentialsError:
            error_msg = "No AWS credentials found"
            print(f"❌ {error_msg}")
            self.test_results['tests']['credentials'] = {
                'success': False,
                'error': error_msg
            }
            return False
        except ClientError as e:
            error_msg = f"AWS credentials error: {e}"
            print(f"❌ {error_msg}")
            self.test_results['tests']['credentials'] = {
                'success': False,
                'error': error_msg
            }
            return False
        except Exception as e:
            error_msg = f"Unexpected credentials error: {e}"
            print(f"❌ {error_msg}")
            self.test_results['tests']['credentials'] = {
                'success': False,
                'error': error_msg
            }
            return False
    
    def test_bucket_access(self):
        """Test bucket access permissions"""
        print(f"\n🪣 Testing bucket access for '{self.bucket_name}'...")
        
        if not self.s3_client:
            print("❌ S3 client not available")
            return False
        
        try:
            # Test bucket head (basic access)
            response = self.s3_client.head_bucket(Bucket=self.bucket_name)
            print("✅ Bucket exists and is accessible")
            
            self.test_results['tests']['bucket_access'] = {
                'success': True,
                'bucket_exists': True,
                'response_metadata': response.get('ResponseMetadata', {})
            }
            
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            if error_code == '404':
                print(f"❌ Bucket '{self.bucket_name}' does not exist or is not accessible")
            elif error_code == '403':
                print(f"❌ Access denied to bucket '{self.bucket_name}'")
            else:
                print(f"❌ Bucket access error ({error_code}): {error_msg}")
            
            self.test_results['tests']['bucket_access'] = {
                'success': False,
                'error_code': error_code,
                'error_message': error_msg,
                'bucket_exists': error_code != '404'
            }
            
            return False
        except Exception as e:
            error_msg = f"Unexpected bucket access error: {e}"
            print(f"❌ {error_msg}")
            self.test_results['tests']['bucket_access'] = {
                'success': False,
                'error': error_msg
            }
            return False
    
    def test_bucket_location(self):
        """Test bucket location"""
        print(f"\n🌍 Testing bucket location...")
        
        if not self.s3_client:
            print("❌ S3 client not available")
            return False
        
        try:
            response = self.s3_client.get_bucket_location(Bucket=self.bucket_name)
            location = response.get('LocationConstraint', 'us-east-1')
            
            if location is None:
                location = 'us-east-1'  # Default region
            
            print(f"✅ Bucket location: {location}")
            
            if location != self.region_name:
                print(f"⚠️  Note: Bucket is in {location}, but we're configured for {self.region_name}")
            
            self.test_results['tests']['bucket_location'] = {
                'success': True,
                'actual_location': location,
                'configured_location': self.region_name,
                'location_match': location == self.region_name
            }
            
            return True
            
        except ClientError as e:
            error_msg = f"Could not get bucket location: {e}"
            print(f"❌ {error_msg}")
            self.test_results['tests']['bucket_location'] = {
                'success': False,
                'error': error_msg
            }
            return False
    
    def test_list_objects(self):
        """Test listing objects in bucket"""
        print(f"\n📋 Testing object listing...")
        
        if not self.s3_client:
            print("❌ S3 client not available")
            return False
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=10  # Limit for testing
            )
            
            object_count = response.get('KeyCount', 0)
            total_objects = response.get('KeyCount', 0)
            
            print(f"✅ Successfully listed objects")
            print(f"✅ Found {object_count} objects (showing max 10)")
            
            if object_count > 0:
                print("📂 Sample objects:")
                for obj in response.get('Contents', [])[:5]:
                    size_kb = obj['Size'] / 1024
                    print(f"   - {obj['Key']} ({size_kb:.1f} KB)")
            
            self.test_results['tests']['list_objects'] = {
                'success': True,
                'object_count': object_count,
                'sample_objects': [obj['Key'] for obj in response.get('Contents', [])[:5]]
            }
            
            return True
            
        except ClientError as e:
            error_msg = f"Could not list objects: {e}"
            print(f"❌ {error_msg}")
            self.test_results['tests']['list_objects'] = {
                'success': False,
                'error': error_msg
            }
            return False
    
    def test_upload_permission(self):
        """Test upload permission with a small test file"""
        print(f"\n⬆️  Testing upload permission...")
        
        if not self.s3_client:
            print("❌ S3 client not available")
            return False
        
        test_key = f"test-uploads/edrs-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        test_content = f"EDRS S3 Test File\nGenerated: {datetime.now().isoformat()}\nBucket: {self.bucket_name}"
        
        try:
            # Upload test file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain',
                Metadata={
                    'test-type': 'edrs-connectivity-test',
                    'generated-by': 'edrs-backend'
                }
            )
            
            print(f"✅ Successfully uploaded test file: {test_key}")
            
            # Try to read it back
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=test_key
            )
            
            content = response['Body'].read().decode('utf-8')
            print(f"✅ Successfully downloaded test file")
            
            # Clean up - delete test file
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=test_key
            )
            
            print(f"✅ Successfully deleted test file")
            
            self.test_results['tests']['upload_permission'] = {
                'success': True,
                'test_key': test_key,
                'upload_success': True,
                'download_success': True,
                'delete_success': True
            }
            
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            if error_code == '403':
                print(f"❌ Upload permission denied")
            else:
                print(f"❌ Upload failed ({error_code}): {error_msg}")
            
            self.test_results['tests']['upload_permission'] = {
                'success': False,
                'error_code': error_code,
                'error_message': error_msg
            }
            
            return False
        except Exception as e:
            error_msg = f"Upload test error: {e}"
            print(f"❌ {error_msg}")
            self.test_results['tests']['upload_permission'] = {
                'success': False,
                'error': error_msg
            }
            return False
    
    def test_django_storage_integration(self):
        """Test Django storage integration"""
        print(f"\n🔗 Testing Django storage integration...")
        
        try:
            from core.storage import RejlersS3Storage
            from django.conf import settings
            
            # Test with current settings
            if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
                current_bucket = settings.AWS_STORAGE_BUCKET_NAME
                print(f"📁 Django configured bucket: {current_bucket}")
                
                if current_bucket == self.bucket_name:
                    print(f"✅ Django bucket matches test bucket")
                else:
                    print(f"⚠️  Django bucket differs from test bucket")
            
            # Try to instantiate storage
            storage = RejlersS3Storage()
            print(f"✅ Django RejlersS3Storage instantiated successfully")
            
            self.test_results['tests']['django_integration'] = {
                'success': True,
                'configured_bucket': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'not-set'),
                'bucket_match': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '') == self.bucket_name
            }
            
            return True
            
        except Exception as e:
            error_msg = f"Django integration error: {e}"
            print(f"❌ {error_msg}")
            self.test_results['tests']['django_integration'] = {
                'success': False,
                'error': error_msg
            }
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results['tests'])
        passed_tests = sum(1 for test in self.test_results['tests'].values() if test.get('success', False))
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed:      {passed_tests}")
        print(f"Failed:      {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n🪣 BUCKET ACCESS STATUS:")
        if self.test_results['tests'].get('bucket_access', {}).get('success', False):
            print(f"✅ Bucket '{self.bucket_name}' is accessible")
        else:
            print(f"❌ Bucket '{self.bucket_name}' is NOT accessible")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results['tests'].items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"  {status} {test_name}")
            if not result.get('success', False) and 'error' in result:
                print(f"      Error: {result['error']}")
    
    def save_results(self, filename=None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"s3_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Could not save results: {e}")
    
    def run_all_tests(self):
        """Run all S3 tests"""
        self.print_header()
        
        # Run tests in order
        tests = [
            self.test_boto3_availability,
            self.test_credentials,
            self.test_bucket_access,
            self.test_bucket_location,
            self.test_list_objects,
            self.test_upload_permission,
            self.test_django_storage_integration,
        ]
        
        for test in tests:
            try:
                test()
            except KeyboardInterrupt:
                print("\n\n⚠️  Test interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error in {test.__name__}: {e}")
        
        self.print_summary()
        self.save_results()


def main():
    """Main test function"""
    # Bucket from ARN: arn:aws:s3:::rejlers-edrs-project
    bucket_name = "rejlers-edrs-project"
    region_name = "us-east-1"  # Default region, will be detected
    
    tester = S3BucketTester(bucket_name, region_name)
    tester.run_all_tests()


if __name__ == "__main__":
    main()