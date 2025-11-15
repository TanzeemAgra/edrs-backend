"""
Simple Contact Form Handler
Standalone view for handling contact form submissions
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def simple_contact_submit(request):
    """
    Simple contact form handler that sends email to Mohammed Agra
    """
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        # Extract form fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        company = data.get('company', '').strip()
        phone = data.get('phone', '').strip()
        inquiry_type = data.get('inquiry_type', 'general')
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        # Basic validation
        if not all([name, email, subject, message]):
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields (Name, Email, Subject, Message)'
            }, status=400)
        
        if '@' not in email:
            return JsonResponse({
                'success': False,
                'message': 'Please provide a valid email address'
            }, status=400)
        
        # Create professional email for Mohammed Agra
        email_subject = f"EDRS Contact Inquiry: {inquiry_type.title()} - {subject}"
        
        email_message = f"""
Dear Mohammed,

A new contact inquiry has been received through the EDRS platform:

═══════════════════════════════════════════════════════════════════════════════
CONTACT DETAILS
═══════════════════════════════════════════════════════════════════════════════
Name: {name}
Email: {email}
Company: {company or 'Not provided'}
Phone: {phone or 'Not provided'}
Inquiry Type: {inquiry_type.title()}

═══════════════════════════════════════════════════════════════════════════════
INQUIRY DETAILS
═══════════════════════════════════════════════════════════════════════════════
Subject: {subject}

Message:
{message}

═══════════════════════════════════════════════════════════════════════════════
SYSTEM INFORMATION
═══════════════════════════════════════════════════════════════════════════════
Submitted: {request.META.get('HTTP_HOST', 'EDRS Platform')}
User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}

═══════════════════════════════════════════════════════════════════════════════

Please respond to the client directly at: {email}

Best regards,
EDRS Notification System
Rejlers Abu Dhabi
        """
        
        # Send email to Mohammed Agra
        try:
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rejlers.ae'),
                recipient_list=['mohammed.agra@rejlers.ae'],
                fail_silently=False,
            )
            
            logger.info(f"Contact form email sent to Mohammed Agra for inquiry from {email}")
            
            response = JsonResponse({
                'success': True,
                'message': 'Thank you for contacting us! Your message has been sent directly to Mohammed Agra at Rejlers Abu Dhabi. We will respond within 24 hours.'
            })
            
        except Exception as email_error:
            logger.error(f"Failed to send contact email: {email_error}")
            
            response = JsonResponse({
                'success': False,
                'message': 'Unable to send email at this time. Please contact mohammed.agra@rejlers.ae directly.',
                'fallback_email': 'mohammed.agra@rejlers.ae'
            }, status=500)
        
        # Add CORS headers
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
        
    except json.JSONDecodeError:
        response = JsonResponse({
            'success': False,
            'message': 'Invalid request format'
        }, status=400)
        response['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        response = JsonResponse({
            'success': False,
            'message': 'Server error. Please try again later.'
        }, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response