from django import forms
from django.core.exceptions import ValidationError
from .models import WaitListUser, RoleChoices, SourceChoices

class WaitlistSignupForm(forms.ModelForm):
    # Removed confirm_email field since you're not using it in template
    
    class Meta:
        model = WaitListUser
        fields = ['name', 'email', 'role', 'source']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your full name',
                'class': 'form-input',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'you@example.com',
                'class': 'form-input',
                'autocomplete': 'email',
            }),
            'role': forms.Select(attrs={
                'class': 'form-select form-input',
            }),
            'source': forms.Select(attrs={
                'class': 'form-select form-input',
            }),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'role': 'I am a',
            'source': 'How did you hear about us?',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add empty default option for role
        self.fields['role'].choices = [('', 'Select your role')] + list(RoleChoices.choices)
        
        # Add empty default option for source
        self.fields['source'].choices = [('', 'Select one')] + list(SourceChoices.choices)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            # Check if email already exists
            if WaitListUser.objects.filter(email=email).exists():
                # We'll handle duplicates in the view
                pass
        return email
    
