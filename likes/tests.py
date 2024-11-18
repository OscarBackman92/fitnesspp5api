from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from workouts.models import Workout
from .models import Like


class LikeTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        self.workout = Workout.objects.create(
            owner=self.user1,
            title='Test Workout',
            workout_type='cardio',
            duration=30
        )
        self.client.login(username='user1', password='pass123')

    def test_can_like_workout(self):
        response = self.client.post('/likes/', {'workout': self.workout.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)

    def test_cant_like_workout_twice(self):
        self.client.post('/likes/', {'workout': self.workout.id})
        response = self.client.post('/likes/', {'workout': self.workout.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_unlike_workout(self):
        like = Like.objects.create(owner=self.user1, workout=self.workout)
        response = self.client.delete(f'/likes/{like.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.count(), 0)
