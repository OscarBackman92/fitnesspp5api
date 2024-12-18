from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100, blank=True, default='Add Name')
    bio = models.TextField(max_length=500, blank=True, default='Add Bio')
    weight = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)], default=0.0)
    height = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)], default=0.0)
    profile_image = models.ImageField(
        upload_to='profile_pictures/', default='default_profile_ylwpgw')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s profile"

    def clean(self):
        """Ensure that date_of_birth is not in the future."""
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")


def create_user_profile(sender, instance, created, **kwargs):
    """Signal to create user profile when user is created."""
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
