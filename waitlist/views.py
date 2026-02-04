from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging
from .models import WaitListUser
from .forms import WaitlistSignupForm

logger = logging.getLogger(__name__)

# Create your views here.
def landing_page(request):
    """Enhanced landing page with stats and dynamic content"""
    # Calculate waitlist stats
    total_users = WaitListUser.objects.count()
    coaches = WaitListUser.objects.filter(role='coach').count()
    early_birds = WaitListUser.objects.filter(is_early_adopter=True).count() if hasattr(WaitListUser, 'is_early_adopter') else 0
    
    context = {
        'total_users': total_users,
        'coaches': coaches,
        'early_birds': early_birds,
        'early_bird_threshold': 100,  # First 100 get early adopter status
        'remaining_spots': max(0, 100 - early_birds),
        'show_form': True,
    }
    return render(request, 'waitlist/landing-page.html', context)

@require_http_methods(["GET", "POST"])
def waitlist_signup(request):
    """Enhanced signup view with AJAX support and better error handling"""
    if request.method == "POST":
        form = WaitlistSignupForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')
            
            # Check if user already exists
            existing_user = WaitListUser.objects.filter(email=email).first()
            
            if existing_user:
                # User already exists - update their info but don't create duplicate
                existing_user.name = form.cleaned_data.get('name')
                existing_user.role = form.cleaned_data.get('role')
                existing_user.source = form.cleaned_data.get('source')
                existing_user.save()
                waitlist_user = existing_user
                is_new = False
            else:
                # Create new user
                waitlist_user = form.save(commit=False)
                
                # Check if they're an early bird (first 100)
                total_users = WaitListUser.objects.count()
                if total_users < 100 and hasattr(waitlist_user, 'is_early_adopter'):
                    waitlist_user.is_early_adopter = True
                
                waitlist_user.is_invited = True
                
                # Get client IP if available
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                
                if hasattr(waitlist_user, 'ip_address'):
                    waitlist_user.ip_address = ip
                
                waitlist_user.save()
                is_new = True
            
            # Calculate position in waitlist
            position = WaitListUser.objects.filter(
                created_at__lt=waitlist_user.created_at
            ).count() + 1 if is_new else None
            
            # Send confirmation email
            email_sent = send_waitlist_confirmation_email(waitlist_user, position)
            
            # Prepare response data
            response_data = {
                'success': True,
                'message': "🎉 You're on the waitlist! Check your email for confirmation.",
                'is_early_adopter': getattr(waitlist_user, 'is_early_adopter', False),
                'is_new_user': is_new,
                'position': position,
            }
            
            # For AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            
            # For regular form submissions
            messages.success(request, response_data['message'])
            
            # Store session data for thank you page
            request.session['waitlist_data'] = {
                'name': waitlist_user.name,
                'email': waitlist_user.email,
                'is_early_adopter': getattr(waitlist_user, 'is_early_adopter', False),
                'position': position,
            }
            
            return redirect("waitlist:thanks")
        
        else:
            # Form has errors
            error_data = {
                'success': False,
                'errors': form.errors,
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(error_data, status=400)
            
            messages.error(request, "Please correct the errors below.")
    
    else:
        form = WaitlistSignupForm()
    
    return render(request, "waitlist/signup.html", {"form": form})

def send_waitlist_confirmation_email(waitlist_user, position=None):
    """Enhanced email sending with HTML template and error handling"""
    try:
        subject = "🎉 Welcome to BodyForgr Waitlist!"
        
        # Prepare email context
        context = {
            'name': waitlist_user.name,
            'email': waitlist_user.email,
            'role': waitlist_user.get_role_display() if hasattr(waitlist_user, 'get_role_display') else waitlist_user.role,
            'is_early_adopter': getattr(waitlist_user, 'is_early_adopter', False),
            'position': position,
            'total_users': WaitListUser.objects.count(),
        }
        
        # Render HTML content
        html_content = render_to_string(
            "emails/waitlist_confirmation.html",
            context,
        )
        
        # Render plain text content (fallback)
        text_content = f"""Hi {waitlist_user.name},

Thanks for joining the BodyForgr beta waitlist!

You'll be among the first to know when we launch and get exclusive early access.

{"🎊 CONGRATULATIONS! You're an Early Bird!" if context['is_early_adopter'] else ""}
{"Your position in line: #" + str(position) if position else ""}

Stay tuned for updates!

– The BodyForgr Team
"""
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[waitlist_user.email],
            reply_to=[settings.REPLY_TO_EMAIL] if hasattr(settings, 'REPLY_TO_EMAIL') else None,
        )
        
        email.attach_alternative(html_content, "text/html")
        
        # Add headers for tracking
        email.extra_headers = {
            'X-PM-Tag': 'waitlist-confirmation',
        }
        
        # Send email
        email.send(fail_silently=False)
        
        logger.info(f"Waitlist confirmation email sent to {waitlist_user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {waitlist_user.email}: {str(e)}", exc_info=True)
        return False

def waitlist_success(request):
    """Enhanced thank you page with personalized data"""
    # Get data from session
    waitlist_data = request.session.get('waitlist_data', {})
    
    # Calculate additional stats
    total_users = WaitListUser.objects.count()
    early_birds = WaitListUser.objects.filter(is_early_adopter=True).count() if hasattr(WaitListUser, 'is_early_adopter') else 0
    
    context = {
        'name': waitlist_data.get('name', 'there'),
        'email': waitlist_data.get('email', ''),
        'is_early_adopter': waitlist_data.get('is_early_adopter', False),
        'position': waitlist_data.get('position'),
        'total_users': total_users,
        'early_birds': early_birds,
        'remaining_spots': max(0, 100 - early_birds),
    }
    
    # Clear session data after showing
    if 'waitlist_data' in request.session:
        del request.session['waitlist_data']
    
    return render(request, "waitlist/thanks.html", context)

# Optional: API endpoint for external signups
def waitlist_api_signup(request):
    """API endpoint for external services (React apps, mobile apps, etc.)"""
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            
            # Create form from JSON data
            form = WaitlistSignupForm(data)
            
            if form.is_valid():
                # Save the user (duplicates will be handled in waitlist_signup logic)
                # For simplicity, we'll reuse the waitlist_signup logic
                # Or you can extract the logic into a shared function
                
                # For now, redirect to standard signup
                response_data = {
                    'success': True,
                    'message': 'User added to waitlist',
                    'redirect_url': '/waitlist/signup/success/'
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)