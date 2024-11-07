from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100, blank=True)
    weight = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    profile_image = CloudinaryField('image', folder='profile_images', default='default_profile_ylwpgw')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_age(self):
        """Calculate age from date_of_birth."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class Goal(models.Model):
    GOAL_TYPES = [
        ('weight', 'Weight Goal'),
        ('workout', 'Workout Frequency'),
        ('strength', 'Strength Goal'),
        ('cardio', 'Cardio Goal'),
        ('custom', 'Custom Goal'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='goals', null=True)
    type = models.CharField(max_length=50, choices=GOAL_TYPES)
    description = models.TextField()
    target = models.CharField(max_length=100)
    deadline = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', '-created_at']

    def __str__(self):
        return f"{self.user_profile.user.username}'s {self.get_type_display()} goal"

    def calculate_progress(self):
        """Calculate goal progress based on completion and deadline."""
        if self.completed:
            return 100
        if self.deadline:
            days_total = (self.deadline - self.created_at.date()).days
            days_passed = (timezone.now().date() - self.created_at.date()).days
            return min(int((days_passed / days_total) * 100), 100) if days_total > 0 else 0
        return 0

def create_user_profile(sender, instance, created, **kwargs):
    """Signal to create user profile when user is created."""
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
