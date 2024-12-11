from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from workouts.models import Workout
from .models import WorkoutPost, Like, Comment
from django.db import transaction


class SocialModelTests(APITestCase):
    """Test suite for social app models."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )

        # Create a test workout
        self.workout = Workout.objects.create(
            owner=self.user1,
            title="Test Workout",
            workout_type="cardio",
            duration=30,
            intensity="moderate",
            date_logged=timezone.now().date()
        )

        # Create a test workout post
        self.workout_post = WorkoutPost.objects.create(
            user=self.user1,
            workout=self.workout
        )

    def test_workout_post_creation(self):
        """Test WorkoutPost model creation."""
        self.assertEqual(self.workout_post.user, self.user1)
        self.assertEqual(self.workout_post.workout, self.workout)
        self.assertTrue(isinstance(self.workout_post, WorkoutPost))
        self.assertEqual(str(self.workout_post),
            f"{self.user1.username}'s cardio workout")

    def test_like_creation(self):
        """Test Like model creation."""
        like = Like.objects.create(
            user=self.user2,
            post=self.workout_post
        )
        self.assertEqual(like.user, self.user2)
        self.assertEqual(like.post, self.workout_post)
        self.assertTrue(isinstance(like, Like))

    def test_comment_creation(self):
        """Test Comment model creation."""
        comment = Comment.objects.create(
            user=self.user2,
            post=self.workout_post,
            content="Great workout!"
        )
        self.assertEqual(comment.user, self.user2)
        self.assertEqual(comment.post, self.workout_post)
        self.assertEqual(comment.content, "Great workout!")
        self.assertTrue(isinstance(comment, Comment))


class SocialViewTests(APITestCase):
    """Test suite for social app views."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )

        # Create a test workout
        self.workout = Workout.objects.create(
            owner=self.user1,
            title="Test Workout",
            workout_type="cardio",
            duration=30,
            intensity="moderate",
            date_logged=timezone.now().date()
        )

        # Create a test workout post
        self.workout_post = WorkoutPost.objects.create(
            user=self.user1,
            workout=self.workout
        )

        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

    def test_list_workout_posts(self):
        """Test listing workout posts."""
        url = reverse('social:feed-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_workout_post(self):
        """Test creating a workout post."""
        url = reverse('social:feed-list')
        data = {
            'workout_id': self.workout.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_like_workout_post(self):
        """Test liking and unliking a workout post."""
        url = reverse('social:feed-like', kwargs={'pk': self.workout_post.id})
        
        # Test liking
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'liked')
        
        # Test unliking
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unliked')

    def test_comment_on_post(self):
        """Test commenting on a workout post."""
        url = reverse('social:feed-comments', kwargs={'pk': self.workout_post.id})
        data = {
            'content': 'Great workout!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Great workout!')
        self.assertTrue(
            Comment.objects.filter(
                content='Great workout!',
                user=self.user1,
                post=self.workout_post
            ).exists()
        )

    def tearDown(self):
        """Clean up test data."""
        Comment.objects.all().delete()
        Like.objects.all().delete()
        WorkoutPost.objects.all().delete()
        Workout.objects.all().delete()
        User.objects.all().delete()