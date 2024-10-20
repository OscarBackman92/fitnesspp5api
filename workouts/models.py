from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Workout(models.Model):
    WORKOUT_TYPES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength Training'),
        ('flexibility', 'Flexibility'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    workout_type = models.CharField(max_length=100, choices=WORKOUT_TYPES)
    date_logged = models.DateField(default=timezone.now)
    duration = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(1440)])  # max 24 hours
    calories = models.IntegerField(validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    intensity = models.CharField(max_length=20, choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')], default='moderate')

    class Meta:
        ordering = ['-date_logged', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_workout_type_display()} on {self.date_logged}"

    def get_duration_in_hours(self):
        return self.duration / 60