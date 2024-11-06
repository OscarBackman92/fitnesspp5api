from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField

class Workout(models.Model):
    # Workout types as class constants
    CARDIO = 'cardio'
    STRENGTH = 'strength'
    FLEXIBILITY = 'flexibility'
    SPORTS = 'sports'
    OTHER = 'other'

    WORKOUT_TYPES = [
        (CARDIO, 'Cardio'),
        (STRENGTH, 'Strength Training'),
        (FLEXIBILITY, 'Flexibility'),
        (SPORTS, 'Sports'),
        (OTHER, 'Other'),
    ]

    # Intensity levels as class constants
    LOW = 'low'
    MODERATE = 'moderate'
    HIGH = 'high'

    INTENSITY_LEVELS = [
        (LOW, 'Low'),
        (MODERATE, 'Moderate'),
        (HIGH, 'High'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workouts'
    )
    workout_type = models.CharField(max_length=100, choices=WORKOUT_TYPES)
    date_logged = models.DateField(default=timezone.now)
    duration = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],  # max 24 hours
        help_text="Duration in minutes"
    )
    calories = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Calories burned"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    intensity = models.CharField(
        max_length=20,
        choices=INTENSITY_LEVELS,
        default=MODERATE
    )
    image = CloudinaryField(
        'image',
        folder='workout_images',
        blank=True,
        null=True,
        transformation={
            'quality': 'auto:eco',
            'crop': 'fill',
            'aspect_ratio': '16:9'
        }
    )

    class Meta:
        ordering = ['-date_logged', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_workout_type_display()} ({self.intensity}) on {self.date_logged}"

    def get_duration_in_hours(self):
        """Convert duration from minutes to hours."""
        return round(self.duration / 60, 2)
