from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserFollow, WorkoutLike, WorkoutComment
from workouts.models import Workout

class SocialFeatureTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.client.force_authenticate(user=self.user1)
        
        # Create test workout
        self.workout = Workout.objects.create(
            user=self.user2,
            workout_type='cardio',
            duration=30,
            calories=300
        )

    def test_follow_user(self):
        response = self.client.post(reverse('follow-follow'), {'user_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserFollow.objects.filter(
            follower=self.user1,
            following=self.user2
        ).exists())

    def test_unfollow_user(self):
        # First follow
        UserFollow.objects.create(follower=self.user1, following=self.user2)
        response = self.client.post(reverse('follow-unfollow'), {'user_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserFollow.objects.filter(
            follower=self.user1,
            following=self.user2
        ).exists())

    def test_like_workout(self):
        response = self.client.post(reverse('like-list'), {'workout': self.workout.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkoutLike.objects.filter(
            user=self.user1,
            workout=self.workout
        ).exists())

    def test_comment_on_workout(self):
        response = self.client.post(reverse('comment-list'), {
            'workout': self.workout.id,
            'content': 'Great workout!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkoutComment.objects.filter(
            user=self.user1,
            workout=self.workout,
            content='Great workout!'
        ).exists())

    def test_get_social_feed(self):
        # Follow user2
        UserFollow.objects.create(follower=self.user1, following=self.user2)
        response = self.client.get(reverse('social-feed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Should see user2's workout

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
        follow = UserFollow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(str(follow), 'user1 follows user2')

    def test_workout_like_string_representation(self):
        like = WorkoutLike.objects.create(user=self.user1, workout=self.workout)
        self.assertEqual(str(like), 'user1 likes user2 - cardio on ' + str(self.workout.date_logged))

    def test_workout_comment_string_representation(self):
        comment = WorkoutComment.objects.create(
            user=self.user1,
            workout=self.workout,
            content='Great workout!'
        )
        self.assertEqual(str(comment), 'Comment by user1 on user2 - cardio on ' + str(self.workout.date_logged))