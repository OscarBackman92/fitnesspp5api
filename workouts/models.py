from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Workout(models.Model):
    """Model to represent a workout."""

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

    LOW = 'low'
    MODERATE = 'moderate'
    HIGH = 'high'

    INTENSITY_LEVELS = [
        (LOW, 'Low'),
        (MODERATE, 'Moderate'),
        (HIGH, 'High'),
    ]

    title = models.CharField(
        max_length=200,
        default="My Workout",
        help_text="Title of the workout"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workouts',
        db_index=True,
        null=True
    )
    workout_type = models.CharField(
        max_length=100,
        choices=WORKOUT_TYPES,
        db_index=True
    )
    date_logged = models.DateField(
        default=timezone.now,
        db_index=True
    )
    duration = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Duration in minutes"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the workout"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    intensity = models.CharField(
        max_length=20,
        choices=INTENSITY_LEVELS,
        default=MODERATE,
        db_index=True
    )

    class Meta:
        ordering = ['-date_logged', '-created_at']
        indexes = [
            models.Index(fields=['owner', 'date_logged']),
            models.Index(fields=['workout_type', 'intensity'])
        ]
        verbose_name = 'Workout'
        verbose_name_plural = 'Workouts'

    def __str__(self):
        return f"{self.title}({self.date_logged})"

    def get_duration_in_hours(self):
        """Convert duration from minutes to hours."""
        return round(self.duration / 60, 2)
