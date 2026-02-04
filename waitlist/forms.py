from django import forms
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import WaitListUser

class WaitlistSignupForm(forms.ModelForm):
    confirm_email = forms.EmailField(
        label="Confirm Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Re-type your email address',
            'class': 'form-input'
        })
    )
    
    class Meta:
        model = WaitListUser
        fields = ['name', 'email', 'role', 'source']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your full name',
                'class': 'form-input',
                'autocomplete': 'name'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'you@example.com',
                'class': 'form-input',
                'autocomplete': 'email'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select',
                'id': 'role-select'
            }),
            'source': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'role': 'I am a',
            'source': 'How did you hear about us?',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')
        
        # Check if emails match
        if email and confirm_email and email != confirm_email:
            self.add_error('confirm_email', "Email addresses don't match.")
        
        # Check for duplicate emails
        if email and WaitListUser.objects.filter(email=email).exists():
            # Don't throw error - just show success to prevent email harvesting
            cleaned_data['email'] = email
            # We'll handle duplicate silently in view
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Basic email validation
            validator = EmailValidator()
            validator(email)
        return email.lower()  # Store emails in lowercase