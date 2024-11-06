# social/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from .models import UserFollow, WorkoutLike, WorkoutComment
from workouts.models import Workout

class SocialTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123',
            email='user1@test.com'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123',
            email='user2@test.com'
        )

        # Create test workout
        self.workout = Workout.objects.create(
            user=self.user2,
            workout_type='cardio',
            duration=30,
            calories=300,
            date_logged=date.today()
        )

        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

    def test_comment_on_workout(self):
        """Test commenting on a workout"""
        response = self.client.post(
            reverse('comment-list'),
            {
                'workout': self.workout.id,
                'content': 'Great workout!'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutComment.objects.count(), 1)
        self.assertEqual(
            WorkoutComment.objects.first().content,
            'Great workout!'
        )

    def test_get_workout_comments(self):
        """Test getting workout comments"""
        # Create exactly two comments
        comments = [
            WorkoutComment.objects.create(
                user=self.user1,
                workout=self.workout,
                content=f'Comment {i}'
            )
            for i in range(2)
        ]
        
        response = self.client.get(
            f"{reverse('comment-list')}?workout_id={self.workout.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data[0]['content'],
            'Comment 1'
        )

    def test_delete_own_comment(self):
        """Test deleting own comment"""
        comment = WorkoutComment.objects.create(
            user=self.user1,
            workout=self.workout,
            content='Test comment'
        )
        
        response = self.client.delete(
            reverse('comment-detail', kwargs={'pk': comment.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(WorkoutComment.objects.count(), 0)

    def test_cannot_delete_others_comment(self):
        """Test cannot delete other user's comment"""
        comment = WorkoutComment.objects.create(
            user=self.user2,
            workout=self.workout,
            content='Test comment'
        )
        
        response = self.client.delete(
            reverse('comment-detail', kwargs={'pk': comment.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(WorkoutComment.objects.count(), 1)
        self.assertTrue(
            WorkoutComment.objects.filter(id=comment.id).exists()
        )

    def test_like_workout(self):
        """Test liking a workout"""
        response = self.client.post(
            reverse('like-list'),
            {'workout': self.workout.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            WorkoutLike.objects.filter(
                user=self.user1,
                workout=self.workout
            ).exists()
        )

    def test_unlike_workout(self):
        """Test unliking a workout"""
        # First create the like
        like = WorkoutLike.objects.create(
            user=self.user1,
            workout=self.workout
        )
        
        response = self.client.post(
            reverse('like-list'),
            {'workout': self.workout.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            WorkoutLike.objects.filter(id=like.id).exists()
        )

    def test_cannot_like_own_workout(self):
        """Test user cannot like their own workout"""
        own_workout = Workout.objects.create(
            user=self.user1,
            workout_type='cardio',
            duration=30,
            calories=300,
            date_logged=date.today()
        )
        
        response = self.client.post(
            reverse('like-list'),
            {'workout': own_workout.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            WorkoutLike.objects.filter(
                user=self.user1,
                workout=own_workout
            ).exists()
        )