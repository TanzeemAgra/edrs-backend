"""
Create User Groups and Roles for Rejlers Abu Dhabi EDRS
Role-based access control for engineering document management
"""

from django.db import migrations
from django.contrib.auth.models import Group, Permission


def create_rejlers_user_groups(apps, schema_editor):
    """
    Create Rejlers Abu Dhabi specific user groups with appropriate permissions
    """
    
    # Define Rejlers Abu Dhabi organizational structure
    groups_permissions = {
        'Project Manager': [
            'add_pidproject', 'change_pidproject', 'delete_pidproject', 'view_pidproject',
            'add_piddiagram', 'change_piddiagram', 'delete_piddiagram', 'view_piddiagram',
            'add_analysisresult', 'change_analysisresult', 'view_analysisresult',
            'view_pidanalysissession', 'add_pidanalysissession',
        ],
        'Senior Engineer': [
            'add_pidproject', 'change_pidproject', 'view_pidproject',
            'add_piddiagram', 'change_piddiagram', 'view_piddiagram',
            'add_analysisresult', 'change_analysisresult', 'view_analysisresult',
            'view_pidanalysissession', 'add_pidanalysissession',
        ],
        'Lead Engineer': [
            'add_pidproject', 'change_pidproject', 'view_pidproject',
            'add_piddiagram', 'change_piddiagram', 'view_piddiagram',
            'add_analysisresult', 'view_analysisresult',
            'view_pidanalysissession', 'add_pidanalysissession',
        ],
        'Principal Engineer': [
            'add_pidproject', 'change_pidproject', 'view_pidproject',
            'add_piddiagram', 'change_piddiagram', 'view_piddiagram',
            'add_analysisresult', 'view_analysisresult',
            'view_pidanalysissession', 'add_pidanalysissession',
        ],
        'Process Engineer': [
            'add_pidproject', 'view_pidproject',
            'add_piddiagram', 'change_piddiagram', 'view_piddiagram',
            'add_analysisresult', 'view_analysisresult',
            'view_pidanalysissession', 'add_pidanalysissession',
        ],
        'Design Engineer': [
            'add_pidproject', 'view_pidproject',
            'add_piddiagram', 'change_piddiagram', 'view_piddiagram',
            'view_analysisresult',
            'view_pidanalysissession',
        ],
        'QA/QC Engineer': [
            'view_pidproject',
            'view_piddiagram',
            'add_analysisresult', 'change_analysisresult', 'view_analysisresult',
            'view_pidanalysissession', 'add_pidanalysissession',
        ],
        'Instrument Engineer': [
            'view_pidproject',
            'add_piddiagram', 'change_piddiagram', 'view_piddiagram',
            'view_analysisresult',
            'view_pidanalysissession',
        ],
        'Mechanical Engineer': [
            'view_pidproject',
            'add_piddiagram', 'view_piddiagram',
            'view_analysisresult',
            'view_pidanalysissession',
        ],
        'Safety Engineer': [
            'view_pidproject',
            'view_piddiagram',
            'add_analysisresult', 'view_analysisresult',
            'view_pidanalysissession', 'add_pidanalysissession',
        ]
    }
    
    # Create groups and assign permissions
    for group_name, permission_codenames in groups_permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)
        
        if created:
            print(f"Created group: {group_name}")
        
        # Clear existing permissions
        group.permissions.clear()
        
        # Add permissions
        for codename in permission_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                print(f"Permission {codename} does not exist")
        
        print(f"Configured permissions for group: {group_name}")


def reverse_create_rejlers_user_groups(apps, schema_editor):
    """
    Remove Rejlers Abu Dhabi user groups
    """
    group_names = [
        'Project Manager', 'Senior Engineer', 'Lead Engineer', 'Principal Engineer',
        'Process Engineer', 'Design Engineer', 'QA/QC Engineer', 
        'Instrument Engineer', 'Mechanical Engineer', 'Safety Engineer'
    ]
    
    for group_name in group_names:
        try:
            group = Group.objects.get(name=group_name)
            group.delete()
            print(f"Deleted group: {group_name}")
        except Group.DoesNotExist:
            print(f"Group {group_name} does not exist")


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('pid_analysis', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_rejlers_user_groups,
            reverse_create_rejlers_user_groups,
        ),
    ]