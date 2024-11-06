from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from workouts.models import Workout

class UserFollow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves.")

class WorkoutLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_likes'
    )
    workout = models.ForeignKey(
        'workouts.Workout',  # Fixed: Properly reference the Workout model
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'workout']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.workout}"

class WorkoutComment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_comments'
    )
    workout = models.ForeignKey(
        'workouts.Workout',  # Fixed: Properly reference the Workout model
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.workout}"