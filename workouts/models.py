from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.db.models import Count


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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workouts',
        db_index=True
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
    image = CloudinaryField(
        'image',
        folder='workout_images',
        blank=True,
        null=True,
        transformation={
            'quality': 'auto:eco',
            'fetch_format': 'auto',
            'secure': True
        }
    )

    class Meta:
        ordering = ['-date_logged', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date_logged']),
            models.Index(fields=['workout_type', 'intensity'])
        ]
        verbose_name = 'Workout'
        verbose_name_plural = 'Workouts'

    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.date_logged})"

    def get_duration_in_hours(self):
        """Convert duration from minutes to hours."""
        return round(self.duration / 60, 2)

    @property
    def likes_count(self):
        """Get the number of likes for this workout."""
        return self.workout_likes_workouts.count()

    @property
    def comments_count(self):
        """Get the number of comments for this workout."""
        return self.workout_comments_workouts.count()


class WorkoutLike(models.Model):
    """Model to represent a like on a workout."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_likes_workouts'
    )
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name='workout_likes_workouts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'workout')
        indexes = [models.Index(fields=['user', 'workout'])]
        verbose_name = 'Workout Like'
        verbose_name_plural = 'Workout Likes'

    def __str__(self):
        return f"{self.user.username} likes {self.workout.title}"


class WorkoutComment(models.Model):
    """Model to represent a comment on a workout."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_comments_workouts'
    )
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name='workout_comments_workouts'
    )
    content = models.TextField(help_text="Comment content")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'workout', 'created_at'])]
        verbose_name = 'Workout Comment'
        verbose_name_plural = 'Workout Comments'

    def __str__(self):
        return f"Comment by {self.user.username} on {self.workout.title}"
