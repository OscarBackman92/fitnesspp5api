from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from .models import UserFollow, WorkoutLike, WorkoutComment
from workouts.models import Workout

class SocialFeatureTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.client.force_authenticate(user=self.user1)
        
        self.workout = Workout.objects.create(
            user=self.user2,
            workout_type='cardio',
            duration=30,
            calories=300
        )

    def test_follow_user(self):
        response = self.client.post(
            reverse('social-follow-follow'),
            {'user_id': self.user2.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unfollow_user(self):
        UserFollow.objects.create(follower=self.user1, following=self.user2)
        response = self.client.post(
            reverse('social-follow-unfollow'),
            {'user_id': self.user2.id}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_like_workout(self):
        response = self.client.post(
            reverse('social-like-list'),
            {'workout': self.workout.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_on_workout(self):
        response = self.client.post(
            reverse('social-comment-list'),
            {
                'workout': self.workout.id,
                'content': 'Great workout!'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class SocialModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.workout = Workout.objects.create(
            user=self.user2,
            workout_type='cardio',
            duration=30,
            calories=300
        )

    def test_user_follow_string_representation(self):
        follow = UserFollow.objects.create(
            follower=self.user1,
            following=self.user2
        )
        self.assertEqual(str(follow), 'user1 follows user2')

    def test_workout_like_string_representation(self):
        like = WorkoutLike.objects.create(
            user=self.user1,
            workout=self.workout
        )
        expected = f'user1 likes {self.workout}'
        self.assertEqual(str(like), expected)

    def test_workout_comment_string_representation(self):
        comment = WorkoutComment.objects.create(
            user=self.user1,
            workout=self.workout,
            content='Great workout!'
        )
        expected = f'Comment by user1 on {self.workout}'
        self.assertEqual(str(comment), expected)