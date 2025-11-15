"""
Django management command to create Rejlers Abu Dhabi test users
Demonstrates role-based S3 folder structure and document access
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.pid_analysis.models import PIDProject, PIDDiagram
from core.storage import get_user_role_folder, get_rejlers_file_path
import os
from datetime import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Create Rejlers Abu Dhabi test users and demonstrate S3 folder structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Create test users for different Rejlers roles',
        )
        parser.add_argument(
            '--show-structure',
            action='store_true',
            help='Show S3 folder structure for all user roles',
        )
        parser.add_argument(
            '--assign-role',
            type=str,
            help='Assign role to existing user (email:role)',
        )

    def handle(self, *args, **options):
        if options['create_users']:
            self.create_test_users()
        
        if options['show_structure']:
            self.show_s3_structure()
        
        if options['assign_role']:
            self.assign_user_role(options['assign_role'])

    def create_test_users(self):
        """Create test users for different Rejlers roles"""
        
        test_users = [
            {
                'email': 'ahmed.hassan@rejlers.ae',
                'first_name': 'Ahmed',
                'last_name': 'Hassan',
                'role': 'Project Manager',
                'password': 'rejlers2025',
            },
            {
                'email': 'fatima.ali@rejlers.ae',
                'first_name': 'Fatima',
                'last_name': 'Ali',
                'role': 'Senior Engineer',
                'password': 'rejlers2025',
            },
            {
                'email': 'mohammed.omar@rejlers.ae',
                'first_name': 'Mohammed',
                'last_name': 'Omar',
                'role': 'Process Engineer',
                'password': 'rejlers2025',
            },
            {
                'email': 'sara.khalil@rejlers.ae',
                'first_name': 'Sara',
                'last_name': 'Khalil',
                'role': 'Design Engineer',
                'password': 'rejlers2025',
            },
        ]
        
        self.stdout.write(self.style.SUCCESS('\n🏗️  Creating Rejlers Abu Dhabi Test Users'))
        self.stdout.write('=' * 60)
        
        for user_data in test_users:
            # Create or get user
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': False,
                    'is_active': True,
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f"✅ Created user: {user_data['first_name']} {user_data['last_name']}")
            else:
                self.stdout.write(f"ℹ️  User exists: {user_data['first_name']} {user_data['last_name']}")
            
            # Assign role
            try:
                group = Group.objects.get(name=user_data['role'])
                user.groups.clear()  # Remove existing groups
                user.groups.add(group)
                self.stdout.write(f"   📋 Assigned role: {user_data['role']}")
                
                # Show S3 folder path
                role_folder = get_user_role_folder(user)
                s3_path = f"rejlers-abudhabi/{role_folder}/{user.id}"
                self.stdout.write(f"   📁 S3 Path: {s3_path}")
                
            except Group.DoesNotExist:
                self.stdout.write(f"   ❌ Role '{user_data['role']}' not found")
            
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('✅ Test users creation completed!'))

    def show_s3_structure(self):
        """Show the complete S3 folder structure for Rejlers Abu Dhabi"""
        
        self.stdout.write(self.style.SUCCESS('\n📁 Rejlers Abu Dhabi S3 Folder Structure'))
        self.stdout.write('=' * 60)
        
        root_folder = 'rejlers-abudhabi'
        
        # Show organizational hierarchy
        role_structure = {
            'administrators': ['Admin users with full access'],
            'project-managers': ['Project Managers', 'Senior Engineers'],
            'lead-engineers': ['Lead Engineers', 'Principal Engineers'],
            'process-engineers': ['Process Engineers'],
            'design-engineers': ['Design Engineers'],
            'qa-qc-engineers': ['QA/QC Engineers'],
            'engineers': ['Other engineering roles']
        }
        
        self.stdout.write(f"\n🏢 {root_folder}/")
        
        for role_folder, roles in role_structure.items():
            self.stdout.write(f"├── 📂 {role_folder}/")
            self.stdout.write(f"│   ├── 👥 Roles: {', '.join(roles)}")
            
            # Show users in this role
            users_in_role = User.objects.filter(
                groups__name__in=roles,
                is_active=True
            ).distinct()
            
            for i, user in enumerate(users_in_role[:3]):  # Show first 3 users
                is_last_user = i == len(users_in_role) - 1 or i == 2
                user_prefix = "└──" if is_last_user else "├──"
                
                self.stdout.write(f"│   {user_prefix} 👤 {user.id}/ ({user.get_full_name() or user.username})")
                self.stdout.write(f"│   {'    ' if is_last_user else '│   '}├── projects/")
                self.stdout.write(f"│   {'    ' if is_last_user else '│   '}│   ├── project_name/")
                self.stdout.write(f"│   {'    ' if is_last_user else '│   '}│   │   ├── pid-diagrams/")
                self.stdout.write(f"│   {'    ' if is_last_user else '│   '}│   │   │   ├── 2025/11/")
                self.stdout.write(f"│   {'    ' if is_last_user else '│   '}│   │   │   └── document.pdf")
                self.stdout.write(f"│   {'    ' if is_last_user else '│   '}│   │   ├── images/")
                self.stdout.write(f"│   {'    ' if is_last_user else '│   '}│   │   ├── documents/")
                self.stdout.write(f"│   {'    ' if is_last_user else '│   '}│   │   └── analysis-results/")
                
                if i < 2 and i < len(users_in_role) - 1:
                    self.stdout.write(f"│   │")
            
            self.stdout.write("│")
        
        # Show example file paths
        self.stdout.write(f"\n📋 Example File Paths:")
        self.stdout.write(f"┌─ Process Engineer Upload:")
        self.stdout.write(f"│  rejlers-abudhabi/process-engineers/123/projects/haradh_expansion/pid-diagrams/2025/11/PID-001_Rev-A.pdf")
        self.stdout.write(f"│")
        self.stdout.write(f"├─ Project Manager Document:")
        self.stdout.write(f"│  rejlers-abudhabi/project-managers/456/projects/lng_terminal/documents/2025/11/Project_Specs.docx")
        self.stdout.write(f"│")
        self.stdout.write(f"└─ Design Engineer Image:")
        self.stdout.write(f"   rejlers-abudhabi/design-engineers/789/projects/pipeline_system/images/2025/11/isometric_view.png")

    def assign_user_role(self, role_assignment):
        """Assign role to existing user"""
        
        try:
            email, role_name = role_assignment.split(':')
            
            user = User.objects.get(email=email)
            group = Group.objects.get(name=role_name)
            
            user.groups.clear()
            user.groups.add(group)
            
            role_folder = get_user_role_folder(user)
            s3_path = f"rejlers-abudhabi/{role_folder}/{user.id}"
            
            self.stdout.write(self.style.SUCCESS(f"✅ Assigned '{role_name}' to {email}"))
            self.stdout.write(f"📁 S3 Path: {s3_path}")
            
        except ValueError:
            self.stdout.write(self.style.ERROR("❌ Format: email:role (e.g., user@rejlers.ae:Process Engineer)"))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ User '{email}' not found"))
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Role '{role_name}' not found"))
            self.stdout.write("Available roles:")
            for group in Group.objects.all():
                self.stdout.write(f"  - {group.name}")

    def create_sample_project(self, user):
        """Create a sample project to demonstrate file paths"""
        
        project, created = PIDProject.objects.get_or_create(
            name="Haradh Gas Plant Expansion",
            created_by=user,
            defaults={
                'description': 'Sample project for testing S3 folder structure',
                'project_type': 'upstream',
                'engineering_standard': 'isa_5_1',
                'field_name': 'Haradh Field',
                'facility_code': 'HGP-EXP',
                'client_company': 'Saudi Aramco',
                'engineering_contractor': 'Rejlers Abu Dhabi',
            }
        )
        
        if created:
            self.stdout.write(f"📊 Created sample project: {project.name}")
            
            # Show what the file path would be
            sample_filename = "PID-HGP-001_Rev-A.pdf"
            file_path = get_rejlers_file_path(project, sample_filename, user)
            self.stdout.write(f"📁 Sample file path: {file_path}")
        
        return project