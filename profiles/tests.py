from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer


class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )

    def test_profile_creation(self):
        """Test profile is created automatically when user is created"""
        self.assertTrue(Profile.objects.filter(owner=self.user).exists())


class ProfileListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )

    def test_can_list_profiles(self):
        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user_can_update_own_profile(self):
        self.client.login(username='testuser', password='testpass123')
        profile = Profile.objects.get(owner=self.user)
        response = self.client.put(
            f'/profiles/{profile.id}/',
            {'name': 'updated name', 'bio': 'updated bio'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'updated name')

    def test_user_cant_update_another_users_profile(self):
        other_user = User.objects.create_user(
            username='testuser2', 
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.put(
            f'/profiles/{other_user.profile.id}/',
            {'name': 'updated name', 'bio': 'updated bio'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)