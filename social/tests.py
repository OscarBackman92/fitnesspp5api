from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserFollow, WorkoutLike, WorkoutComment
from workouts.models import Workout
from datetime import date

class UserFollowAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass')  # Add this line
        self.client.force_authenticate(user=self.user)

    def test_follow_user(self):
        url = reverse('userfollow-toggle-follow')
        response = self.client.post(url, {'user_id': self.other_user.id})
        self.assertEqual(response.status_code, 201)

    def test_unfollow_user(self):
        self.client.post(reverse('userfollow-toggle-follow'), {'user_id': self.other_user.id})
        url = reverse('userfollow-toggle-follow')
        response = self.client.post(url, {'user_id': self.other_user.id})
        self.assertEqual(response.status_code, 200) 

class WorkoutLikeAPITests(TestCase):
    """Test suite for WorkoutLike API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.workout = Workout.objects.create(
            user=self.user,
            workout_type='cardio',
            date_logged=date.today(),
            duration=30
        )
        self.client.force_authenticate(user=self.user)

    def test_like_workout(self):
        """Test liking a workout."""
        url = reverse('workoutlike-list')
        response = self.client.post(url, {'workout': self.workout.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkoutLike.objects.filter(user=self.user, workout=self.workout).exists())

    def test_unlike_workout(self):
        """Test unliking a workout."""
        WorkoutLike.objects.create(user=self.user, workout=self.workout)
        url = reverse('workoutlike-list')
        response = self.client.post(url, {'workout': self.workout.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(WorkoutLike.objects.filter(user=self.user, workout=self.workout).exists())

class WorkoutCommentAPITests(TestCase):
    """Test suite for WorkoutComment API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.workout = Workout.objects.create(
            user=self.user,
            workout_type='cardio',
            date_logged=date.today(),
            duration=30
        )
        self.client.force_authenticate(user=self.user)

    def test_add_comment(self):
        """Test adding a comment to a workout."""
        url = reverse('workoutcomment-list')
        response = self.client.post(url, {'workout': self.workout.id, 'content': 'Great workout!'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkoutComment.objects.filter(user=self.user, workout=self.workout).exists())

    def test_delete_comment(self):
        """Test deleting a comment."""
        comment = WorkoutComment.objects.create(user=self.user, workout=self.workout, content='Nice!')
        url = reverse('workoutcomment-detail', kwargs={'pk': comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(WorkoutComment.objects.filter(id=comment.id).exists())
