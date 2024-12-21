from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile
from django.urls import reverse
from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch


class UserProfileModelTestCase(TestCase):
    """Tests for the UserProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")

    def test_user_profile_creation(self):
        profile = UserProfile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)

    def test_date_of_birth_validation(self):
        profile = UserProfile.objects.get(user=self.user)
        profile.date_of_birth = date.today() + timedelta(days=1)  # Future date
        with self.assertRaises(Exception) as e:
            profile.clean()
        self.assertIn("Date of birth cannot be in the future.", str(e.exception))


class UserProfileAPITestCase(APITestCase):
    """Tests for the UserProfile API"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.profile = UserProfile.objects.get(user=self.user)

    def test_retrieve_user_profile(self):
        url = reverse("api:profile-detail", kwargs={"pk": self.profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_update_user_profile(self):
        url = reverse("api:profile-detail", kwargs={"pk": self.profile.id})
        response = self.client.patch(url, {"bio": "Updated bio"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "Updated bio")
