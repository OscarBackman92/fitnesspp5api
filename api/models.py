from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    fitness_goals = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=100)
    date_logged = models.DateField()
    duration = models.IntegerField()
    calories = models.IntegerField()

    def __str__(self):
        return f"{self.user} - {self.workout_type} on {self.date_logged}"
