"""
Test AWS SES Email Configuration
Management command to test email sending to Mohammed Agra
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test AWS SES email configuration for contact form'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipient',
            type=str,
            default='mohammed.agra@rejlers.ae',
            help='Email recipient to test with',
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        
        self.stdout.write('🧪 Testing AWS SES Email Configuration')
        self.stdout.write('=' * 60)
        
        # Check email settings
        self.stdout.write(f"📧 Email Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"📤 From Email: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not configured')}")
        self.stdout.write(f"📥 Test Recipient: {recipient}")
        
        if hasattr(settings, 'USE_AWS_SES') and settings.USE_AWS_SES:
            self.stdout.write(f"🌍 AWS SES Region: {getattr(settings, 'AWS_SES_REGION_NAME', 'Not configured')}")
        
        # Send test email
        try:
            subject = "EDRS Contact Form Test - AWS SES Configuration"
            message = f"""
Dear Mohammed,

This is a test email to verify the EDRS contact form email configuration.

═══════════════════════════════════════════════════════════════
TEST DETAILS
═══════════════════════════════════════════════════════════════
Test Date: {self.get_current_time()}
Email Backend: {settings.EMAIL_BACKEND}
From Email: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not configured')}
Recipient: {recipient}

═══════════════════════════════════════════════════════════════
SYSTEM STATUS
═══════════════════════════════════════════════════════════════
✅ Contact form backend API: Operational
✅ Email configuration: Loaded
✅ AWS SES integration: {'Enabled' if getattr(settings, 'USE_AWS_SES', False) else 'Disabled'}

═══════════════════════════════════════════════════════════════

If you received this email, the contact form email system is working correctly.

Best regards,
EDRS Email System
Rejlers Abu Dhabi
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rejlers.ae'),
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Test email sent successfully to {recipient}'))
            self.stdout.write(f'📧 Check {recipient} for the test message')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to send test email: {e}'))
            self.stdout.write('')
            self.stdout.write('🔧 Troubleshooting steps:')
            self.stdout.write('1. Check AWS credentials in .env.local')
            self.stdout.write('2. Verify AWS SES region configuration')
            self.stdout.write('3. Ensure sender email is verified in AWS SES')
            self.stdout.write('4. Check django-ses package installation')
    
    def get_current_time(self):
        """Get current time in a readable format"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')


# Simple email test without Django management command
def test_contact_email():
    """Simple function to test email configuration"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        send_mail(
            subject='EDRS Contact Test',
            message='Test message from EDRS contact form system.',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rejlers.ae'),
            recipient_list=['mohammed.agra@rejlers.ae'],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email test failed: {e}")
        return False