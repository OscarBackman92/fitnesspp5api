from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    weight = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(500)])
    height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(300)])
    fitness_goals = models.TextField(null=True, blank=True)
    profile_picture = CloudinaryField('image', 
                                      folder='profile_pictures', 
                                      default='default_profile_ylwpgw',
                                      blank=True, 
                                      null=True)
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

# Add to your existing api/models.py
class Goal(models.Model):
    GOAL_TYPES = [
        ('weight', 'Weight Goal'),
        ('workout', 'Workout Frequency'),
        ('strength', 'Strength Goal'),
        ('cardio', 'Cardio Goal'),
        ('custom', 'Custom Goal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    type = models.CharField(max_length=50, choices=GOAL_TYPES)
    description = models.TextField()
    target = models.CharField(max_length=100)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()}"

class Measurement(models.Model):
    MEASUREMENT_TYPES = [
        ('weight', 'Weight'),
        ('chest', 'Chest'),
        ('waist', 'Waist'),
        ('hips', 'Hips'),
        ('biceps', 'Biceps'),
        ('thighs', 'Thighs'),
        ('calves', 'Calves')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='measurements')
    type = models.CharField(max_length=50, choices=MEASUREMENT_TYPES)
    value = models.FloatField()
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()}: {self.value}"