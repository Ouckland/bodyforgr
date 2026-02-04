from django.db import models

class RoleChoices(models.TextChoices):
    USER = 'user', 'User'
    COACH = 'coach', 'Coach'

class SourceChoices(models.TextChoices):
    HOMEPAGE = 'homepage', 'Homepage'
    TWITTER = 'x', 'X (formerly Twitter)'
    SOCIAL_MEDIA = 'other_social_media', 'Other Social Media'
    FRIEND = 'friend_referral', 'Friend Referral'
    OTHER = 'other', 'Other'

class WaitListUser(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=RoleChoices.choices)
    source = models.CharField(max_length=50, choices=SourceChoices.choices, blank=True, null=True)
    
    # New fields
    is_early_adopter = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_invited = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.role}"
    
    def save(self, *args, **kwargs):
        # Make email lowercase before saving
        self.email = self.email.lower()
        super().save(*args, **kwargs)
    
    @property
    def waitlist_position(self):
        """Calculate position in waitlist"""
        return WaitListUser.objects.filter(
            created_at__lt=self.created_at
        ).count() + 1
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Waitlist User'
        verbose_name_plural = 'Waitlist Users'