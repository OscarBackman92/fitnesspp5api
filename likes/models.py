from django.db import models
from django.contrib.auth.models import User
from workouts.models import Workout


class Like(models.Model):
    """
    Like model, related to User and Workout.
    'unique_together' makes sure a user can't like the same workout twice.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(
        Workout, related_name='likes', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['owner', 'workout']

    def __str__(self):
        return f'{self.owner} likes {self.workout}'
