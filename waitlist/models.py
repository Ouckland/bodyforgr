from django.db import models

# Create your models here.

class role_choices(models.TextChoices):
    user = 'user', 'User'
    coach = 'coach', 'Coach'

def source_choices():
    return [
        ('homepage', 'Homepage'),
        ('x', 'X (formerly Twitter)'),
        ('other_social_media', 'Other Social Media'),
        ('friend_referral', 'Friend Referral'),
        ('other', 'Other'),
    ]

class WaitListUser(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(choices=role_choices.choices, max_length=10, blank=False, null=False)
    is_invited = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    source = models.CharField(choices=source_choices(), max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.role}"
    
    class Meta:
        ordering = ['-created_at']
