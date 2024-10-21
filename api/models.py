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

