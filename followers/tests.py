from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Follower


class FollowerTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', 
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            password='pass123'
        )
        self.client.login(username='user1', password='pass123')

    def test_can_follow_user(self):
        response = self.client.post(
            '/followers/',
            {'followed': self.user2.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follower.objects.count(), 1)

    def test_cant_follow_user_twice(self):
        self.client.post('/followers/', {'followed': self.user2.id})
        response = self.client.post(
            '/followers/',
            {'followed': self.user2.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_unfollow_user(self):
        follower = Follower.objects.create(
            owner=self.user1,
            followed=self.user2
        )
        response = self.client.delete(f'/followers/{follower.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Follower.objects.count(), 0)

    def test_cant_follow_self(self):
        response = self.client.post(
            '/followers/',
            {'followed': self.user1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)