from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserFollow, WorkoutLike, WorkoutComment
from workouts.models import Workout

class SocialAPITests(TestCase):
    """Test suite for Social API endpoints"""

    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass123')
        self.user3 = User.objects.create_user(username='user3', email='user3@test.com', password='pass123')

        # Create test workouts
        self.workout1 = Workout.objects.create(user=self.user2, workout_type='cardio', duration=30, calories=300, date_logged='2024-11-01')
        self.workout2 = Workout.objects.create(user=self.user2, workout_type='strength', duration=45, calories=400, date_logged='2024-11-02')

        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

    def test_follow_functionality(self):
        """Test all aspects of follow functionality"""
        response = self.client.post(reverse('toggle-follow'), {'user_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserFollow.objects.filter(follower=self.user1, following=self.user2).exists())

        response = self.client.post(reverse('toggle-follow'), {'user_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(UserFollow.objects.filter(follower=self.user1, following=self.user2).exists())

        response = self.client.post(reverse('toggle-follow'), {'user_id': 99999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.post(reverse('toggle-follow'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse('toggle-follow'), {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_functionality(self):
        """Test all aspects of like functionality"""
        response = self.client.post(reverse('like-list'), {'workout': self.workout1.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(self.workout1.likes.count(), 1)

        response = self.client.post(reverse('like-list'), {'workout': self.workout1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.workout1.likes.count(), 0)

        response = self.client.post(reverse('like-list'), {'workout': 99999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.post(reverse('like-list'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_functionality(self):
        """Test all aspects of comment functionality"""
        # Clear existing comments before testing
        WorkoutComment.objects.all().delete()  

        response = self.client.post(reverse('comment-list'), {'workout': self.workout1.id, 'content': 'Great workout!'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(reverse('comment-list'), {'workout_id': self.workout1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only have one comment

    def test_feed_functionality(self):
        """Test social feed functionality"""
        UserFollow.objects.create(follower=self.user1, following=self.user2)

        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if workout1 is included in the feed from user2
        self.assertIn(self.workout1.id, [w['id'] for w in response.data])

    def test_social_statistics(self):
        """Test social statistics endpoints"""
        UserFollow.objects.create(follower=self.user1, following=self.user2)
        UserFollow.objects.create(follower=self.user3, following=self.user1)
        WorkoutLike.objects.create(user=self.user1, workout=self.workout1)
        WorkoutComment.objects.create(user=self.user1, workout=self.workout1, content='Test comment')

        response = self.client.get(reverse('followers-count'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['followers_count'], 1)

        response = self.client.get(reverse('following-count'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following_count'], 1)

        response = self.client.get(reverse('workout-detail', kwargs={'pk': self.workout1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)
        self.assertEqual(response.data['comments_count'], 1)

    def test_authentication_required(self):
        """Test authentication requirements"""
        client = APIClient()  # Unauthenticated client
        
        protected_urls = [
            reverse('toggle-follow'),
            reverse('like-list'),
            reverse('comment-list'),
            reverse('feed'),
        ]
        
        for url in protected_urls:
            response = client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            response = client.post(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
