#!/usr/bin/env python3
"""
Simple AWS S3 Bucket Access Test
Tests access to arn:aws:s3:::rejlers-edrs-project
"""

import os
import sys
from datetime import datetime

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    print(f"✅ boto3 version: {boto3.__version__}")
except ImportError as e:
    print(f"❌ boto3 not available: {e}")
    sys.exit(1)

def test_s3_bucket_access(bucket_name="rejlers-edrs-project"):
    """
    Test AWS S3 bucket access with multiple credential methods
    """
    
    print("=" * 60)
    print("🔍 AWS S3 BUCKET ACCESS TEST")
    print("=" * 60)
    print(f"Bucket Name: {bucket_name}")
    print(f"Bucket ARN:  arn:aws:s3:::{bucket_name}")
    print(f"Test Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Try different credential methods
    credential_methods = [
        ("Environment Variables", test_env_credentials),
        ("AWS Profile", test_profile_credentials),
        ("Manual Input", test_manual_credentials),
    ]
    
    s3_client = None
    
    for method_name, test_func in credential_methods:
        print(f"\n🔐 Testing {method_name}...")
        s3_client = test_func()
        if s3_client:
            print(f"✅ {method_name} successful")
            break
        else:
            print(f"❌ {method_name} failed")
    
    if not s3_client:
        print("\n❌ No valid AWS credentials found")
        print("\n💡 To test S3 access, you need AWS credentials:")
        print("   1. Set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("   2. Configure AWS CLI: aws configure")
        print("   3. Use IAM roles (if running on AWS)")
        return False
    
    # Test bucket operations
    return test_bucket_operations(s3_client, bucket_name)


def test_env_credentials():
    """Test environment variable credentials"""
    if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        try:
            s3_client = boto3.client('s3')
            # Test credentials
            s3_client.list_buckets()
            return s3_client
        except Exception as e:
            print(f"   Environment credentials error: {e}")
    return None


def test_profile_credentials():
    """Test AWS profile credentials"""
    try:
        # Try default profile first
        s3_client = boto3.client('s3')
        s3_client.list_buckets()
        return s3_client
    except Exception as e:
        print(f"   AWS profile error: {e}")
    return None


def test_manual_credentials():
    """Test with manually entered credentials"""
    print("\n   Enter AWS credentials for testing:")
    
    access_key = input("   AWS Access Key ID: ").strip()
    secret_key = input("   AWS Secret Access Key: ").strip()
    region = input("   AWS Region [us-east-1]: ").strip() or "us-east-1"
    
    if not access_key or not secret_key:
        print("   Skipping manual credentials")
        return None
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        # Test credentials
        s3_client.list_buckets()
        return s3_client
    except Exception as e:
        print(f"   Manual credentials error: {e}")
    return None


def test_bucket_operations(s3_client, bucket_name):
    """Test bucket operations"""
    
    print(f"\n🪣 Testing bucket '{bucket_name}' operations...")
    
    # Test 1: Check if bucket exists
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print("✅ Bucket exists and is accessible")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Bucket '{bucket_name}' does not exist")
            return False
        elif error_code == '403':
            print(f"❌ Access denied to bucket '{bucket_name}'")
            return False
        else:
            print(f"❌ Bucket error ({error_code}): {e.response['Error']['Message']}")
            return False
    
    # Test 2: Get bucket location
    try:
        response = s3_client.get_bucket_location(Bucket=bucket_name)
        location = response.get('LocationConstraint') or 'us-east-1'
        print(f"✅ Bucket location: {location}")
    except ClientError as e:
        print(f"⚠️  Could not get bucket location: {e}")
    
    # Test 3: List objects
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
        object_count = response.get('KeyCount', 0)
        print(f"✅ Successfully listed objects: {object_count} found (max 5 shown)")
        
        if object_count > 0:
            print("📂 Sample objects:")
            for obj in response.get('Contents', []):
                size_mb = obj['Size'] / (1024 * 1024)
                print(f"   - {obj['Key']} ({size_mb:.2f} MB)")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            print(f"⚠️  Cannot list objects (permission denied)")
        else:
            print(f"⚠️  Cannot list objects: {e}")
    
    # Test 4: Test upload (if possible)
    test_key = f"test-uploads/edrs-access-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=f"EDRS S3 Access Test\nGenerated: {datetime.now().isoformat()}",
            ContentType='text/plain'
        )
        print(f"✅ Upload test successful: {test_key}")
        
        # Clean up
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print(f"✅ Cleanup successful")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            print(f"⚠️  Upload test failed (permission denied)")
        else:
            print(f"⚠️  Upload test failed: {e}")
    
    print("\n✅ S3 bucket access test completed successfully!")
    return True


def main():
    """Main function"""
    bucket_name = "rejlers-edrs-project"
    
    print("This script will test access to the AWS S3 bucket:")
    print(f"ARN: arn:aws:s3:::{bucket_name}")
    print("\nPress Enter to continue or Ctrl+C to exit...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        return
    
    success = test_s3_bucket_access(bucket_name)
    
    if success:
        print("\n🎉 SUCCESS: S3 bucket is accessible!")
    else:
        print("\n❌ FAILED: S3 bucket is not accessible")
        print("\n💡 Next steps:")
        print("   1. Verify bucket name and ARN")
        print("   2. Check AWS credentials")
        print("   3. Verify bucket permissions and policies")
        print("   4. Ensure bucket exists in the correct region")


if __name__ == "__main__":
    main()