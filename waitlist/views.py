from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging
import json
from .models import WaitListUser
from .forms import WaitlistSignupForm

logger = logging.getLogger(__name__)

# Constants
EARLY_BIRD_LIMIT = 100

# Create your views here.
def landing_page(request):
    """Main landing page with waitlist form"""
    # Calculate waitlist stats
    total_users = WaitListUser.objects.count()
    coaches = WaitListUser.objects.filter(role='coach').count()
    early_birds = WaitListUser.objects.filter(is_early_adopter=True).count()
    
    context = {
        'total_users': total_users,
        'coaches': coaches,
        'early_birds': early_birds,
        'remaining_spots': max(0, EARLY_BIRD_LIMIT - early_birds),
    }
    return render(request, 'waitlist/landing-page.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def waitlist_signup(request):
    """
    Handle waitlist signup (AJAX only)
    Since you're using a single page, this should only handle AJAX requests
    """
    form = WaitlistSignupForm(request.POST)
    
    if form.is_valid():
        email = form.cleaned_data['email'].lower()
        
        # Check for existing user
        existing_user = WaitListUser.objects.filter(email=email).first()
        
        if existing_user:
            # Update existing user
            existing_user.name = form.cleaned_data['name']
            existing_user.role = form.cleaned_data['role']
            existing_user.source = form.cleaned_data['source']
            existing_user.save()
            waitlist_user = existing_user
            is_new = False
            position = existing_user.waitlist_position
        else:
            # Create new user
            waitlist_user = form.save(commit=False)
            
            # Check if early bird
            total_users = WaitListUser.objects.count()
            if total_users < EARLY_BIRD_LIMIT:
                waitlist_user.is_early_adopter = True
            
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            waitlist_user.ip_address = ip
            waitlist_user.is_invited = True
            waitlist_user.save()
            
            is_new = True
            position = waitlist_user.waitlist_position
        
        # Send confirmation email
        email_sent = send_confirmation_email(waitlist_user, position, is_new)
        
        # Prepare response data
        response_data = {
            'success': True,
            'message': "You're on the waitlist! Check your email for confirmation.",
            'is_early_adopter': waitlist_user.is_early_adopter,
            'is_new_user': is_new,
            'position': position,
            'total_users': WaitListUser.objects.count(),
        }
        
        # Log the signup
        logger.info(f"Waitlist signup: {email} - {'New' if is_new else 'Existing'} user")
        
        return JsonResponse(response_data)
    
    else:
        # Form has errors
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

def send_confirmation_email(waitlist_user, position, is_new_user=True):
    """Send waitlist confirmation email"""
    try:
        subject = "Welcome to BodyForgr Waitlist!"
        
        # Prepare context
        context = {
            'user': waitlist_user,
            'position': position if is_new_user else None,
            'is_early_adopter': waitlist_user.is_early_adopter,
            'total_users': WaitListUser.objects.count(),
        }
        
        # Render email content
        html_content = render_to_string(
            "emails/waitlist_confirmation.html",
            context
        )
        text_content = strip_tags(html_content)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[waitlist_user.email],
            html_message=html_content,
            fail_silently=True,
        )
        
        logger.info(f"Confirmation email sent to {waitlist_user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {waitlist_user.email}: {str(e)}")
        return False

def waitlist_success(request):
    """Thank you page (for non-AJAX submissions or direct access)"""
    # Get data from session or show generic message
    waitlist_data = request.session.get('waitlist_data', {})
    
    context = {
        'name': waitlist_data.get('name', 'there'),
        'email': waitlist_data.get('email', ''),
        'is_early_adopter': waitlist_data.get('is_early_adopter', False),
        'position': waitlist_data.get('position'),
    }
    
    # Clear session data
    if 'waitlist_data' in request.session:
        del request.session['waitlist_data']
    
    return render(request, "waitlist/thanks.html", context)

@csrf_exempt
def waitlist_api_signup(request):
    """Public API endpoint for external services"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        form = WaitlistSignupForm(data)
        
        if form.is_valid():
            # Process similar to regular signup
            email = form.cleaned_data['email'].lower()
            existing_user = WaitListUser.objects.filter(email=email).first()
            
            if existing_user:
                existing_user.name = form.cleaned_data['name']
                existing_user.role = form.cleaned_data['role']
                existing_user.source = form.cleaned_data['source']
                existing_user.save()
                is_new = False
                position = existing_user.waitlist_position
            else:
                waitlist_user = form.save(commit=False)
                total_users = WaitListUser.objects.count()
                if total_users < EARLY_BIRD_LIMIT:
                    waitlist_user.is_early_adopter = True
                waitlist_user.is_invited = True
                waitlist_user.save()
                is_new = True
                position = waitlist_user.waitlist_position
            
            # Send email
            send_confirmation_email(
                existing_user if existing_user else waitlist_user,
                position,
                is_new
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Successfully added to waitlist',
                'position': position,
                'is_early_adopter': (existing_user if existing_user else waitlist_user).is_early_adopter
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"API signup error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)