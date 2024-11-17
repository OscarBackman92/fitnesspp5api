from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.db.models import Count
<<<<<<< HEAD

=======
>>>>>>> 49de782 (feat: Add title field and optimize workout models)

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

<<<<<<< HEAD
    title = models.CharField(max_length=200, default="My Workout", help_text="Title of the workout")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts', db_index=True)
    workout_type = models.CharField(max_length=100, choices=WORKOUT_TYPES, db_index=True)
    date_logged = models.DateField(default=timezone.now, db_index=True)
    duration = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(1440)], help_text="Duration in minutes")
    notes = models.TextField(blank=True, help_text="Additional notes about the workout")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    intensity = models.CharField(max_length=20, choices=INTENSITY_LEVELS, default=MODERATE, db_index=True)
    image = CloudinaryField('image', folder='workout_images', blank=True, null=True, transformation={
        'quality': 'auto:eco', 'fetch_format': 'auto', 'secure': True
    })
=======
    title = models.CharField(
        max_length=200, 
        default="My Workout",
        help_text="Title of the workout"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workouts',
        db_index=True  # Add index for better query performance
    )
    workout_type = models.CharField(
        max_length=100, 
        choices=WORKOUT_TYPES,
        db_index=True  # Add index for filtering and ordering
    )
    date_logged = models.DateField(
        default=timezone.now,
        db_index=True  # Add index for date queries
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
        db_index=True  # Add index for filtering
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
>>>>>>> 49de782 (feat: Add title field and optimize workout models)

    class Meta:
        ordering = ['-date_logged', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date_logged']),  # Compound index for user queries
<<<<<<< HEAD
            models.Index(fields=['workout_type', 'intensity'])  # Index for filtering
=======
            models.Index(fields=['workout_type', 'intensity'])
>>>>>>> 49de782 (feat: Add title field and optimize workout models)
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

<<<<<<< HEAD

class WorkoutLike(models.Model):
    """Model to represent a like on a workout."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_likes_workouts')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_likes_workouts')
=======
class WorkoutLike(models.Model):
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
>>>>>>> 49de782 (feat: Add title field and optimize workout models)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'workout')
<<<<<<< HEAD
        indexes = [models.Index(fields=['user', 'workout'])]
=======
        indexes = [
            models.Index(fields=['user', 'workout'])
        ]
>>>>>>> 49de782 (feat: Add title field and optimize workout models)
        verbose_name = 'Workout Like'
        verbose_name_plural = 'Workout Likes'

    def __str__(self):
        return f"{self.user.username} likes {self.workout.title}"
<<<<<<< HEAD


class WorkoutComment(models.Model):
    """Model to represent a comment on a workout."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_comments_workouts')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_comments_workouts')
    content = models.TextField(help_text="Comment content")
=======

class WorkoutComment(models.Model):
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
    content = models.TextField(
        help_text="Comment content"
    )
>>>>>>> 49de782 (feat: Add title field and optimize workout models)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
<<<<<<< HEAD
        indexes = [models.Index(fields=['user', 'workout', 'created_at'])]
=======
        indexes = [
            models.Index(fields=['user', 'workout', 'created_at'])
        ]
>>>>>>> 49de782 (feat: Add title field and optimize workout models)
        verbose_name = 'Workout Comment'
        verbose_name_plural = 'Workout Comments'

    def __str__(self):
<<<<<<< HEAD
        return f"Comment by {self.user.username} on {self.workout.title}"
=======
        return f"Comment by {self.user.username} on {self.workout.title}"
>>>>>>> 49de782 (feat: Add title field and optimize workout models)
