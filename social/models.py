from django.db import models
from django.contrib.auth.models import User
from workouts.models import Workout


class WorkoutPost(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='workout_posts')
    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Workout Post'
        verbose_name_plural = 'Workout Posts'

    def __str__(self):
        return f"{self.user.username}'s {self.workout.workout_type} workout"


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(
        WorkoutPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.post}"


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(
        WorkoutPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s comment on {self.post}"