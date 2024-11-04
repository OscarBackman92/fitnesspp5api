# api/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    name = models.CharField(max_length=100, blank=True)
    weight = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(500)]
    )
    height = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(300)]
    )
    fitness_goals = models.TextField(null=True, blank=True)
    profile_image = CloudinaryField(
        'image',
        folder='profile_images',
        transformation={
            'quality': 'auto:eco',
            'crop': 'fill',
            'aspect_ratio': '1.0',
            'gravity': 'face'
        },
        format='webp',
        default='default_profile_ylwpgw'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['gender']),
        ]

    def __str__(self):
        return f"{self.user.username}'s profile"

    def calculate_bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.weight and self.height:
            height_m = self.height / 100  # convert cm to m
            return round(self.weight / (height_m ** 2), 2)
        return None

    def get_age(self):
        """Calculate age from date_of_birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < 
                (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def get_goals(self):
        """
        Helper method to get user's goals
        """
        return self.user.goals.all()

    def get_workouts(self):
        """
        Helper method to get user's workouts
        """
        return self.user.workouts.all()

class Goal(models.Model):
    GOAL_TYPES = [
        ('weight', 'Weight Goal'),
        ('workout', 'Workout Frequency'),
        ('strength', 'Strength Goal'),
        ('cardio', 'Cardio Goal'),
        ('custom', 'Custom Goal'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='goals'  # This matches the prefetch_related in the view
    )
    type = models.CharField(max_length=50, choices=GOAL_TYPES)
    description = models.TextField()
    target = models.CharField(max_length=100)
    deadline = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', '-created_at']
        indexes = [
            models.Index(fields=['user', 'type']),
            models.Index(fields=['deadline']),
            models.Index(fields=['completed']),
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.get_type_display()} goal"

def create_user_profile(sender, instance, created, **kwargs):
    """Signal to create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)