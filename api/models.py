from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    weight = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(500)])
    height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(300)])
    fitness_goals = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def calculate_bmi(self):
        if self.weight and self.height:
            return self.weight / ((self.height / 100) ** 2)
        return None

    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

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
