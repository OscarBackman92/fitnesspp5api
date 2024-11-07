from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile, Goal
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile, Goal
from datetime import date, timedelta

class UserProfileAPITests(TestCase):
    """Test suite for UserProfile API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create UserProfile
        self.profile, created = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'name': 'Test User',
                'weight': 70.5,
                'height': 175,
                'date_of_birth': date(1990, 1, 1),
                'gender': 'M'
            }
        )

        # Print profile details for debugging
        print(f"Profile created: {self.profile.name}, {self.profile.weight}, {self.profile.height}, {self.profile.gender}")

        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """Test retrieving the user profile"""
        url = reverse('profile-detail', kwargs={'pk': self.profile.pk})
        response = self.client.get(url)
        print(response.data)  # Print the response data for debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test User')

    def test_update_profile(self):
        """Test updating the user profile"""
        url = reverse('profile-detail', kwargs={'pk': self.profile.pk})
        data = {
            'name': 'Updated Name',
            'weight': 72.5,
            'height': 180
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'Updated Name')
        self.assertEqual(self.profile.weight, 72.5)
        self.assertEqual(self.profile.height, 180)

    def test_upload_profile_image(self):
        """Test profile image upload"""
        url = reverse('profile-upload-image', kwargs={'pk': self.profile.pk})
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        response = self.client.post(url, {'profile_image': image})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile_image', response.data)

    def test_profile_stats(self):
        """Test profile statistics endpoint"""
        url = reverse('profile-stats', kwargs={'pk': self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_workouts', response.data)
        self.assertIn('total_calories', response.data)
        self.assertIn('avg_duration', response.data)
