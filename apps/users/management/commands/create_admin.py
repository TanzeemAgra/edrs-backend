"""
Create and configure the admin user with Rejlers role
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin user with Project Manager role for Rejlers Abu Dhabi'

    def handle(self, *args, **options):
        # Create admin user
        user, created = User.objects.get_or_create(
            email='tanzeem@rejlers.ae',
            defaults={
                'username': 'tanzeem@rejlers.ae',
                'first_name': 'Tanzeem',
                'last_name': 'Ahmed',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        
        if created:
            user.set_password('rejlers2025')
            user.save()
            self.stdout.write(self.style.SUCCESS('✅ Created admin user: tanzeem@rejlers.ae'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️  Admin user already exists'))
        
        # Assign Project Manager role
        try:
            group = Group.objects.get(name='Project Manager')
            user.groups.clear()
            user.groups.add(group)
            self.stdout.write(self.style.SUCCESS('✅ Assigned Project Manager role'))
            
            # Show S3 path
            from core.storage import get_user_role_folder
            role_folder = get_user_role_folder(user)
            s3_path = f"rejlers-abudhabi/{role_folder}/{user.id}"
            self.stdout.write(f"📁 S3 Path: {s3_path}")
            
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Project Manager role not found"))
            self.stdout.write("Available roles:")
            for group in Group.objects.all():
                self.stdout.write(f"  - {group.name}")
        
        self.stdout.write(f"\n🔑 Login Credentials:")
        self.stdout.write(f"   Email: tanzeem@rejlers.ae")
        self.stdout.write(f"   Password: rejlers2025")
        self.stdout.write(f"   Role: Project Manager")
        self.stdout.write(f"   Admin: Yes")