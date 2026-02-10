from threading import Thread
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.utils import IntegrityError
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




def landing_page(request):
    """Main landing page with waitlist form"""
    total_users = WaitListUser.objects.count()
    coaches = WaitListUser.objects.filter(role='coach').count()
    early_birds = WaitListUser.objects.filter(is_early_adopter=True).count()
    
    context = {
        'total_users': total_users,
        'coaches': coaches,
        'early_birds': early_birds,
        'remaining_spots': max(0, 100 - early_birds),
        'form': WaitlistSignupForm(),
    }
    return render(request, 'waitlist/landing-page.html', context)



def send_email_async(waitlist_user, position, is_new_user):
    """Send email in a background thread"""
    try:
        send_confirmation_email(waitlist_user, position, is_new_user)
    except Exception as e:
        logger.warning(f"Async email failed: {str(e)}")
    

@csrf_exempt
@require_http_methods(["POST"])
def waitlist_signup(request):
    """
    Handle waitlist signup (AJAX)
    Redirects to thank you page on success
    """
    form = WaitlistSignupForm(request.POST)

    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

    email = form.cleaned_data['email'].lower()
    name = form.cleaned_data['name']
    role = form.cleaned_data['role']
    source = form.cleaned_data.get('source')

    try:
        with transaction.atomic():
            waitlist_user, created = WaitListUser.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'role': role,
                    'source': source,
                    'is_invited': True,
                }
            )

            if not created:
                # Update existing user info
                waitlist_user.name = name
                waitlist_user.role = role
                waitlist_user.source = source
                waitlist_user.save()
            else:
                # Early bird logic
                total_users = WaitListUser.objects.count()
                if total_users <= EARLY_BIRD_LIMIT:
                    waitlist_user.is_early_adopter = True

                # Get IP address
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
                waitlist_user.ip_address = ip
                waitlist_user.save()

            # Send email asynchronously
            position = waitlist_user.waitlist_position
            Thread(
                target=send_email_async,
                args=(waitlist_user, position, created),
                daemon=True
            ).start()

            # Save some session data for the thanks page
            request.session['waitlist_data'] = {
                'name': name,
                'email': email,
                'position': position,
                'is_early_adopter': waitlist_user.is_early_adopter,
            }

            # Return JSON pointing to redirect URL
            return JsonResponse({
                'success': True,
                'redirect_url': '/waitlist/thanks/'
            })

    except IntegrityError:
        return JsonResponse({
            'success': False,
            'error': 'This email is already on the waitlist.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in waitlist signup: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)




def send_confirmation_email(waitlist_user, position=None, is_new_user=True):
    """Send waitlist confirmation email"""
    try:
        subject = "Welcome to BodyForgr Waitlist!"
        
        # Prepare context
        context = {
            'user': waitlist_user,
            'position': position if is_new_user else None,
            'is_early_adopter': waitlist_user.is_early_adopter,
            'total_users': WaitListUser.objects.count(),
            'unsubscribe_link': '#',
            'privacy_link': '#',
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
            fail_silently=False,
        )
        
        logger.info(f"Confirmation email sent to {waitlist_user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {waitlist_user.email}: {str(e)}")
        return False


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

        if not form.is_valid():
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

        email = form.cleaned_data['email'].lower()
        existing_user = WaitListUser.objects.filter(email=email).first()

        if existing_user:
            existing_user.name = form.cleaned_data['name']
            existing_user.role = form.cleaned_data['role']
            existing_user.source = form.cleaned_data['source']
            existing_user.save()
            is_new = False
            user_to_email = existing_user
            position = existing_user.waitlist_position
        else:
            waitlist_user = form.save(commit=False)
            total_users = WaitListUser.objects.count()
            if total_users < EARLY_BIRD_LIMIT:
                waitlist_user.is_early_adopter = True
            waitlist_user.is_invited = True
            waitlist_user.save()
            is_new = True
            user_to_email = waitlist_user
            position = waitlist_user.waitlist_position

        # Send email asynchronously in a separate thread
        Thread(
            target=send_confirmation_email,
            args=(user_to_email, position, is_new),
            daemon=True
        ).start()

        return JsonResponse({
            'success': True,
            'message': 'Successfully added to waitlist',
            'position': position,
            'is_early_adopter': user_to_email.is_early_adopter
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"API signup error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)
    

def waitlist_success(request):
    """Thank you page for successful signup"""
    # Try to get data from session (for non-AJAX submissions)
    waitlist_data = request.session.get('waitlist_data', {})
    
    # Also check for query parameters (for direct links)
    name = request.GET.get('name', waitlist_data.get('name', 'there'))
    email = request.GET.get('email', waitlist_data.get('email', ''))
    is_early_adopter = request.GET.get('early', 
        str(waitlist_data.get('is_early_adopter', False)).lower()) == 'true'
    position = request.GET.get('position', waitlist_data.get('position'))
    
    # Clear session data after use
    if 'waitlist_data' in request.session:
        del request.session['waitlist_data']
    
    # Get stats for the page
    total_users = WaitListUser.objects.count()
    early_birds = WaitListUser.objects.filter(is_early_adopter=True).count()
    
    context = {
        'name': name,
        'email': email,
        'is_early_adopter': is_early_adopter,
        'position': position,
        'total_users': total_users,
        'early_birds': early_birds,
        'remaining_spots': max(0, EARLY_BIRD_LIMIT - early_birds),
    }
    
    return render(request, "waitlist/thanks.html", context)


def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)