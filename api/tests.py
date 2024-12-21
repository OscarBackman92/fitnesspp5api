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
        print("Setting up UserProfileModelTestCase...")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        print(f"Created test user: {self.user.username}")

    def test_user_profile_creation(self):
        print("Testing user profile creation...")
        profile = UserProfile.objects.get(user=self.user)
        print(f"Retrieved profile for user: {self.user.username}")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)
        print("User profile creation test passed.")

    def test_date_of_birth_validation(self):
        print("Testing date of birth validation...")
        profile = UserProfile.objects.get(user=self.user)
        profile.date_of_birth = date.today() + timedelta(days=1)  # Future date
        print(f"Set date_of_birth to future date: {profile.date_of_birth}")
        with self.assertRaises(Exception) as e:
            profile.clean()
        print(f"Raised exception: {str(e.exception)}")
        self.assertIn("Date of birth cannot be in the future.", str(e.exception))
        print("Date of birth validation test passed.")


class UserProfileAPITestCase(APITestCase):
    """Tests for the UserProfile API"""

    def setUp(self):
        print("Setting up UserProfileAPITestCase...")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        print(f"Created test user: {self.user.username}")
        self.client.force_authenticate(user=self.user)
        print(f"Authenticated client with user: {self.user.username}")
        self.profile = UserProfile.objects.get(user=self.user)
        print(f"Retrieved profile for user: {self.user.username}")

    def test_retrieve_user_profile(self):
        print("Testing retrieve user profile...")
        url = reverse("api:profile-detail", kwargs={"pk": self.profile.id})
        print(f"Retrieve URL: {url}")
        response = self.client.get(url)
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        print("Retrieve user profile test passed.")

    def test_update_user_profile(self):
        print("Testing update user profile...")
        url = reverse("api:profile-detail", kwargs={"pk": self.profile.id})
        print(f"Update URL: {url}")
        response = self.client.patch(url, {"bio": "Updated bio"})
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        print(f"Updated profile bio: {self.profile.bio}")
        self.assertEqual(self.profile.bio, "Updated bio")
        print("Update user profile test passed.")
