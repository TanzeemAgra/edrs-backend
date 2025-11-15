"""
EDRS Storage Configuration
Handles both local and AWS S3 storage configurations with role-based access
"""

import os
from datetime import datetime
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import get_user_model
from storages.backends.s3boto3 import S3Boto3Storage

User = get_user_model()


class RejlersS3Storage(S3Boto3Storage):
    """
    Custom S3 storage for Rejlers Abu Dhabi EDRS
    Implements role-based folder structure and user access control
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    custom_domain = False
    file_overwrite = False
    default_acl = 'private'
    
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'querystring_auth': True,
            'querystring_expire': 7200,  # 2 hours for engineering documents
        })
        super().__init__(*args, **kwargs)
    
    def get_object_parameters(self, name):
        """
        Enhanced object parameters for Rejlers engineering documents
        """
        params = super().get_object_parameters(name)
        
        # Set content type and disposition based on file extension
        if name.lower().endswith(('.pdf', '.dwg', '.dxf')):
            params['ContentType'] = 'application/octet-stream'
            params['ContentDisposition'] = f'attachment; filename="{os.path.basename(name)}"'
        elif name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            params['ContentType'] = 'image/*'
            params['ContentDisposition'] = 'inline'
        elif name.lower().endswith('.zip'):
            params['ContentType'] = 'application/zip'
        
        # Add Rejlers-specific metadata
        params['Metadata'] = {
            'organization': 'rejlers-abudhabi',
            'upload-source': 'edrs-system',
            'file-type': 'engineering-document',
            'upload-date': datetime.now().isoformat(),
        }
        
        # Add cache control for different file types
        if name.lower().endswith(('.pdf', '.dwg', '.dxf')):
            params['CacheControl'] = 'max-age=86400'  # 24 hours for engineering docs
        else:
            params['CacheControl'] = 'max-age=3600'   # 1 hour for other files
        
        return params


class EDRSLocalStorage(FileSystemStorage):
    """
    Custom local storage for EDRS development
    Organizes files by type and project
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_valid_name(self, name):
        """
        Clean and organize file names
        """
        # Keep original filename structure for local development
        return super().get_valid_name(name)


def get_storage_backend():
    """
    Returns appropriate storage backend based on configuration
    """
    if getattr(settings, 'USE_S3', False):
        return EDRSMediaStorage()
    else:
        return EDRSLocalStorage()


# Rejlers Abu Dhabi Role-Based Storage Paths
def get_user_role_folder(user):
    """
    Determines user role folder based on user permissions and groups
    """
    if user.is_superuser:
        return 'administrators'
    elif hasattr(user, 'groups') and user.groups.filter(name__in=['Project Manager', 'Senior Engineer']).exists():
        return 'project-managers'
    elif hasattr(user, 'groups') and user.groups.filter(name__in=['Lead Engineer', 'Principal Engineer']).exists():
        return 'lead-engineers'
    elif hasattr(user, 'groups') and user.groups.filter(name='Process Engineer').exists():
        return 'process-engineers'
    elif hasattr(user, 'groups') and user.groups.filter(name='Design Engineer').exists():
        return 'design-engineers'
    elif hasattr(user, 'groups') and user.groups.filter(name='QA/QC Engineer').exists():
        return 'qa-qc-engineers'
    else:
        return 'engineers'


def get_rejlers_file_path(instance, filename, user=None):
    """
    Generates Rejlers Abu Dhabi organized file paths with role-based access
    Structure: rejlers-abudhabi/{role}/{user_id}/{project}/{document_type}/{year}/{month}/{filename}
    """
    root_folder = getattr(settings, 'AWS_S3_ROOT_FOLDER', 'rejlers-abudhabi')
    
    # Get user from instance or parameter
    if user is None:
        if hasattr(instance, 'created_by'):
            user = instance.created_by
        elif hasattr(instance, 'project') and hasattr(instance.project, 'created_by'):
            user = instance.project.created_by
        else:
            user_folder = 'system'
            user_id = 'system'
    
    if user and user != 'system':
        role_folder = get_user_role_folder(user)
        user_id = str(user.id)
        user_folder = f"{role_folder}/{user_id}"
    else:
        user_folder = 'system'
    
    # Get project information
    if hasattr(instance, 'project') and instance.project:
        project_name = instance.project.name.replace(' ', '_').replace('/', '-').lower()
        project_folder = f"projects/{project_name}"
    elif hasattr(instance, 'name') and instance.name:
        project_name = instance.name.replace(' ', '_').replace('/', '-').lower()
        project_folder = f"projects/{project_name}"
    else:
        project_folder = "general"
    
    # Determine document type
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    if file_ext in ['pdf', 'dwg', 'dxf']:
        doc_type = 'pid-diagrams'
    elif file_ext in ['png', 'jpg', 'jpeg', 'tiff']:
        doc_type = 'images'
    elif file_ext in ['doc', 'docx', 'xls', 'xlsx']:
        doc_type = 'documents'
    elif file_ext in ['zip', 'rar']:
        doc_type = 'archives'
    else:
        doc_type = 'misc'
    
    # Add date organization
    now = datetime.now()
    date_path = f"{now.year}/{now.month:02d}"
    
    # Clean filename
    clean_filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
    
    # Construct full path
    full_path = f"{root_folder}/{user_folder}/{project_folder}/{doc_type}/{date_path}/{clean_filename}"
    
    return full_path


def get_file_upload_path(instance, filename):
    """
    Main file upload path generator for Rejlers Abu Dhabi
    """
    return get_rejlers_file_path(instance, filename)


def get_analysis_result_path(instance, filename):
    """
    Path for analysis result files with user context
    """
    if hasattr(instance, 'diagram') and hasattr(instance.diagram, 'project'):
        # Use the diagram's project context
        temp_instance = type('temp', (), {
            'project': instance.diagram.project,
            'created_by': getattr(instance.diagram, 'created_by', None)
        })()
        base_path = get_rejlers_file_path(temp_instance, filename)
        # Replace the document type with results
        path_parts = base_path.split('/')
        if len(path_parts) >= 6:
            path_parts[-3] = 'analysis-results'  # Replace doc_type with analysis-results
            return '/'.join(path_parts)
    
    return get_rejlers_file_path(instance, filename)


class DocumentUploadHelper:
    """
    Helper class for document upload operations
    """
    
    ALLOWED_EXTENSIONS = {
        'pdf': ['application/pdf'],
        'dwg': ['application/acad', 'application/x-autocad', 'application/octet-stream'],
        'dxf': ['application/dxf', 'application/x-autocad', 'text/plain'],
        'png': ['image/png'],
        'jpg': ['image/jpeg'],
        'jpeg': ['image/jpeg'],
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @classmethod
    def validate_file(cls, uploaded_file):
        """
        Validate uploaded file type and size
        """
        errors = []
        
        # Check file size
        if uploaded_file.size > cls.MAX_FILE_SIZE:
            errors.append(f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (50MB)")
        
        # Check file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in cls.ALLOWED_EXTENSIONS:
            errors.append(f"File type '{file_extension}' is not supported")
        
        # Check MIME type if possible
        if hasattr(uploaded_file, 'content_type'):
            allowed_mimes = cls.ALLOWED_EXTENSIONS.get(file_extension, [])
            if uploaded_file.content_type not in allowed_mimes:
                # Some browsers send different MIME types, so this is a warning, not an error
                pass
        
        return errors
    
    @classmethod
    def get_file_info(cls, uploaded_file):
        """
        Extract file information
        """
        return {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'content_type': getattr(uploaded_file, 'content_type', 'application/octet-stream'),
            'extension': uploaded_file.name.split('.')[-1].lower(),
        }


# Configuration for different environments
STORAGE_CONFIGS = {
    'local': {
        'backend': 'core.storage.EDRSLocalStorage',
        'options': {
            'location': settings.MEDIA_ROOT,
            'base_url': settings.MEDIA_URL,
        }
    },
    'production': {
        'backend': 'core.storage.EDRSMediaStorage',
        'options': {
            'bucket_name': settings.AWS_STORAGE_BUCKET_NAME,
            'region_name': settings.AWS_S3_REGION_NAME,
        }
    }
}