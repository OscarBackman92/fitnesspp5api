from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Workout(models.Model):
    """
    Workout model, related to User
    """
    WORKOUT_TYPES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength Training'),
        ('flexibility', 'Flexibility'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField()
    workout_type = models.CharField(
        max_length=32, choices=WORKOUT_TYPES, default='other'
    )
    image = CloudinaryField(
        'image',
        folder='workout_images',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.id} {self.title}'

class WorkoutComment(models.Model):
    """
    Comment model, related to User and Workout
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.content

class WorkoutLike(models.Model):
    """
    Like model, related to User and Workout
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['owner', 'workout']

    def __str__(self):
        return f'{self.owner} {self.workout}'