from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import UserFollow, WorkoutLike, WorkoutComment
from workouts.models import Workout

class SocialModelTests(TestCase):
    """Test suite for Social models"""

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='pass123'
        )
        # Create test workout
        self.workout = Workout.objects.create(
            user=self.user2,
            workout_type='cardio',
            duration=30,
            calories=300,
            date_logged=date.today()
        )

    def test_user_follow_model(self):
        """Test UserFollow model creation and constraints"""
        # Test successful follow creation
        follow = UserFollow.objects.create(
            follower=self.user1,
            following=self.user2
        )
        self.assertTrue(isinstance(follow, UserFollow))
        self.assertEqual(
            str(follow),
            f"{self.user1.username} follows {self.user2.username}"
        )

        # Test unique constraint
        with self.assertRaises(Exception):
            UserFollow.objects.create(
                follower=self.user1,
                following=self.user2
            )

        # Test self-follow prevention
        with self.assertRaises(Exception):
            UserFollow.objects.create(
                follower=self.user1,
                following=self.user1
            )

    def test_workout_like_model(self):
        """Test WorkoutLike model creation and constraints"""
        # Test successful like creation
        like = WorkoutLike.objects.create(
            user=self.user1,
            workout=self.workout
        )
        self.assertTrue(isinstance(like, WorkoutLike))
        self.assertEqual(
            str(like),
            f"{self.user1.username} likes {self.workout}"
        )

        # Test unique constraint
        with self.assertRaises(Exception):
            WorkoutLike.objects.create(
                user=self.user1,
                workout=self.workout
            )

    def test_workout_comment_model(self):
        """Test WorkoutComment model creation and methods"""
        comment = WorkoutComment.objects.create(
            user=self.user1,
            workout=self.workout,
            content='Test comment'
        )
        self.assertTrue(isinstance(comment, WorkoutComment))
        self.assertEqual(
            str(comment),
            f"Comment by {self.user1.username} on {self.workout}"
        )
        # Test timestamps
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)

class SocialAPITests(TestCase):
    """Test suite for Social API endpoints"""

    def setUp(self):
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='pass123'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='pass123'
        )

        # Create test workouts
        self.workout = Workout.objects.create(
            user=self.user2,
            workout_type='cardio',
            duration=30,
            calories=300,
            date_logged=date.today()
        )
        self.workout2 = Workout.objects.create(
            user=self.user2,
            workout_type='strength',
            duration=45,
            calories=400,
            date_logged=date.today()
        )

        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

    def test_follow_functionality(self):
        """Test all aspects of follow functionality"""
        # Test following a user
        response = self.client.post(
            reverse('toggle-follow'),
            {'user_id': self.user2.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserFollow.objects.filter(
                follower=self.user1,
                following=self.user2
            ).exists()
        )

        # Test following already followed user
        response = self.client.post(
            reverse('toggle-follow'),
            {'user_id': self.user2.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            UserFollow.objects.filter(
                follower=self.user1,
                following=self.user2
            ).exists()
        )

        # Test following non-existent user
        response = self.client.post(
            reverse('toggle-follow'),
            {'user_id': 99999}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test following without user_id
        response = self.client.post(reverse('toggle-follow'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test following yourself
        response = self.client.post(
            reverse('toggle-follow'),
            {'user_id': self.user1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_functionality(self):
        """Test all aspects of like functionality"""
        # Test liking a workout
        response = self.client.post(
            reverse('like-list'),
            {'workout': self.workout.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test like count
        self.assertEqual(self.workout.likes.count(), 1)

        # Test liking same workout again (unlike)
        response = self.client.post(
            reverse('like-list'),
            {'workout': self.workout.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.workout.likes.count(), 0)

        # Test liking non-existent workout
        response = self.client.post(
            reverse('like-list'),
            {'workout': 99999}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test liking without workout id
        response = self.client.post(reverse('like-list'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_functionality(self):
        """Test all aspects of comment functionality"""
        # Test creating a comment
        response = self.client.post(
            reverse('comment-list'),
            {
                'workout': self.workout.id,
                'content': 'Great workout!'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test getting comments for a workout
        response = self.client.get(
            reverse('comment-list'),
            {'workout_id': self.workout.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test comment ordering (newest first)
        comment2 = WorkoutComment.objects.create(
            user=self.user1,
            workout=self.workout,
            content='Second comment'
        )
        response = self.client.get(
            reverse('comment-list'),
            {'workout_id': self.workout.id}
        )
        self.assertEqual(response.data[0]['content'], 'Second comment')

        # Test empty content
        response = self.client.post(
            reverse('comment-list'),
            {
                'workout': self.workout.id,
                'content': ''
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test very long content
        response = self.client.post(
            reverse('comment-list'),
            {
                'workout': self.workout.id,
                'content': 'x' * 1001  # Assuming max_length=1000
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_permissions(self):
        """Test comment permission handling"""
        # Create comments by different users
        comment1 = WorkoutComment.objects.create(
            user=self.user1,
            workout=self.workout,
            content='User 1 comment'
        )
        comment2 = WorkoutComment.objects.create(
            user=self.user2,
            workout=self.workout,
            content='User 2 comment'
        )

        # Test deleting own comment
        response = self.client.delete(
            reverse('comment-detail', kwargs={'pk': comment1.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Test deleting other's comment
        response = self.client.delete(
            reverse('comment-detail', kwargs={'pk': comment2.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test deleting non-existent comment
        response = self.client.delete(
            reverse('comment-detail', kwargs={'pk': 99999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_feed_functionality(self):
        """Test social feed functionality"""
        # Create follow relationship
        UserFollow.objects.create(follower=self.user1, following=self.user2)

        # Test feed content
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both workouts from user2

        # Test feed ordering (newest first)
        self.assertEqual(
            response.data[0]['id'],
            self.workout2.id
        )

        # Test feed filtering
        response = self.client.get(
            reverse('feed'),
            {'workout_type': 'cardio'}
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['workout_type'],
            'cardio'
        )

    def test_social_statistics(self):
        """Test social statistics endpoints"""
        # Create test data
        UserFollow.objects.create(follower=self.user1, following=self.user2)
        UserFollow.objects.create(follower=self.user3, following=self.user1)
        WorkoutLike.objects.create(user=self.user1, workout=self.workout)
        WorkoutComment.objects.create(
            user=self.user1,
            workout=self.workout,
            content='Test comment'
        )

        # Test followers count
        response = self.client.get(reverse('followers-count'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['followers_count'], 1)

        # Test following count
        response = self.client.get(reverse('following-count'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following_count'], 1)

        # Test workout interaction counts
        response = self.client.get(
            reverse('workout-detail', kwargs={'pk': self.workout.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)
        self.assertEqual(response.data['comments_count'], 1)

    def test_authentication_required(self):
        """Test authentication requirements"""
        client = APIClient()  # Unauthenticated client
        
        # Test unauthenticated access to protected endpoints
        protected_urls = [
            reverse('toggle-follow'),
            reverse('like-list'),
            reverse('comment-list'),
            reverse('feed'),
        ]
        
        for url in protected_urls:
            response = client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED
            )
            response = client.post(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED
            )