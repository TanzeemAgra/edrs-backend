"""
S3 Configuration and Test Endpoints for EDRS
Provides S3 connection testing and configuration validation
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import os

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


@csrf_exempt
@require_http_methods(["GET", "POST"])
def test_s3_connection(request):
    """
    Test S3 connection and bucket access
    """
    try:
        if not BOTO3_AVAILABLE:
            return JsonResponse({
                'success': False,
                'error': 'boto3 not available',
                'message': 'AWS SDK (boto3) is not installed'
            }, status=500)
        
        # Get S3 configuration
        use_s3 = getattr(settings, 'USE_S3', False)
        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
        region_name = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
        
        if not use_s3:
            return JsonResponse({
                'success': False,
                'error': 'S3 not enabled',
                'message': 'S3 storage is not enabled in Django settings',
                'config': {
                    'USE_S3': use_s3,
                    'bucket_name': bucket_name,
                    'region_name': region_name
                }
            }, status=400)
        
        if not bucket_name:
            return JsonResponse({
                'success': False,
                'error': 'No bucket configured',
                'message': 'AWS_STORAGE_BUCKET_NAME not set in settings'
            }, status=400)
        
        # Test credentials and bucket access
        try:
            s3_client = boto3.client('s3', region_name=region_name)
            
            # Test bucket access
            s3_client.head_bucket(Bucket=bucket_name)
            
            # Get bucket location
            location_response = s3_client.get_bucket_location(Bucket=bucket_name)
            actual_region = location_response.get('LocationConstraint') or 'us-east-1'
            
            # Test list objects
            list_response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            object_count = list_response.get('KeyCount', 0)
            
            return JsonResponse({
                'success': True,
                'message': 'S3 connection successful',
                'config': {
                    'bucket_name': bucket_name,
                    'configured_region': region_name,
                    'actual_region': actual_region,
                    'region_match': actual_region == region_name,
                    'object_count': object_count,
                    'USE_S3': use_s3
                },
                'tests': {
                    'bucket_accessible': True,
                    'credentials_valid': True,
                    'list_objects': True
                }
            })
            
        except NoCredentialsError:
            return JsonResponse({
                'success': False,
                'error': 'No credentials',
                'message': 'AWS credentials not found. Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY'
            }, status=401)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == '404':
                message = f'Bucket "{bucket_name}" does not exist'
            elif error_code == '403':
                message = f'Access denied to bucket "{bucket_name}"'
            else:
                message = f'AWS error ({error_code}): {error_message}'
            
            return JsonResponse({
                'success': False,
                'error': f'AWS error: {error_code}',
                'message': message,
                'config': {
                    'bucket_name': bucket_name,
                    'region_name': region_name
                }
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Unexpected error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def s3_config_info(request):
    """
    Get current S3 configuration information
    """
    try:
        config = {
            'USE_S3': getattr(settings, 'USE_S3', False),
            'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None),
            'AWS_S3_REGION_NAME': getattr(settings, 'AWS_S3_REGION_NAME', None),
            'AWS_S3_ROOT_FOLDER': getattr(settings, 'AWS_S3_ROOT_FOLDER', None),
            'DEFAULT_FILE_STORAGE': getattr(settings, 'DEFAULT_FILE_STORAGE', None),
            'boto3_available': BOTO3_AVAILABLE,
            'credentials_available': bool(
                os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY')
            )
        }
        
        return JsonResponse({
            'success': True,
            'config': config,
            'message': 'S3 configuration retrieved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Configuration error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def enable_s3_storage(request):
    """
    Enable S3 storage for the current session (development only)
    """
    try:
        data = json.loads(request.body) if request.body else {}
        enable = data.get('enable', True)
        
        # This would typically be done via environment variables
        # For testing purposes, we can temporarily modify settings
        if hasattr(settings, 'USE_S3'):
            original_value = settings.USE_S3
            # Note: This doesn't persist across requests in production
            settings.USE_S3 = enable
            
            return JsonResponse({
                'success': True,
                'message': f'S3 storage {"enabled" if enable else "disabled"} for this session',
                'config': {
                    'USE_S3': enable,
                    'previous_value': original_value,
                    'note': 'This change is temporary for this session only'
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Configuration error',
                'message': 'USE_S3 setting not found'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Request error',
            'message': str(e)
        }, status=400)