from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal
from .models import UserProfile, Goal
from .serializers import (
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserInfoSerializer,
    GoalSerializer
)
import json
from unittest import mock

class UserProfileModelTests(TestCase):
    """Test suite for UserProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            name='Test User',
            weight=70.5,
            height=175,
            date_of_birth=date(1990, 1, 1),
            gender='M',
            fitness_goals='Get stronger'
        )

    def test_profile_creation(self):
        """Test UserProfile creation and string representation"""
        self.assertTrue(isinstance(self.profile, UserProfile))
        self.assertEqual(str(self.profile), "testuser's profile")
        self.assertTrue(hasattr(self.profile, 'profile_image'))

    def test_calculate_bmi(self):
        """Test BMI calculation with various inputs"""
        # Test normal BMI
        self.assertAlmostEqual(self.profile.calculate_bmi(), 23.02, places=2)

        # Test with zero height
        self.profile.height = 0
        self.assertIsNone(self.profile.calculate_bmi())

        # Test with None values
        self.profile.weight = None
        self.assertIsNone(self.profile.calculate_bmi())

    def test_get_age(self):
        """Test age calculation with various dates"""
        # Test normal age calculation
        today = date.today()
        expected_age = today.year - 1990
        if today < date(today.year, 1, 1):
            expected_age -= 1
        self.assertEqual(self.profile.get_age(), expected_age)

        # Test with None date_of_birth
        self.profile.date_of_birth = None
        self.assertIsNone(self.profile.get_age())

        # Test with future date
        self.profile.date_of_birth = date.today() + timedelta(days=1)
        self.assertEqual(self.profile.get_age(), 0)

    def test_profile_signal(self):
        """Test profile creation signal"""
        new_user = User.objects.create_user(
            username='newuser',
            password='newpass123'
        )
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertTrue(isinstance(new_user.profile, UserProfile))

class UserProfileSerializerTests(TestCase):
    """Test suite for UserProfile serializers"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            name='Test User',
            weight=70.5,
            height=175,
            date_of_birth=date(1990, 1, 1),
            gender='M'
        )

    def test_user_profile_serializer(self):
        """Test UserProfileSerializer"""
        serializer = UserProfileSerializer(instance=self.profile)
        data = serializer.data

        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['name'], 'Test User')
        self.assertAlmostEqual(float(data['weight']), 70.5)
        self.assertEqual(data['height'], 175)
        self.assertEqual(data['gender'], 'M')
        self.assertIn('bmi', data)
        self.assertIn('age', data)

    def test_user_profile_serializer_validation(self):
        """Test UserProfileSerializer validation"""
        # Test invalid weight
        invalid_data = {
            'weight': -50,
            'height': 175
        }
        serializer = UserProfileSerializer(
            instance=self.profile,
            data=invalid_data,
            partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('weight', serializer.errors)

        # Test invalid height
        invalid_data = {
            'weight': 70,
            'height': 0
        }
        serializer = UserProfileSerializer(
            instance=self.profile,
            data=invalid_data,
            partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('height', serializer.errors)

        # Test invalid gender
        invalid_data = {'gender': 'X'}
        serializer = UserProfileSerializer(
            instance=self.profile,
            data=invalid_data,
            partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('gender', serializer.errors)

class UserRegistrationTests(TestCase):
    """Test suite for user registration"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    def test_successful_registration(self):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_invalid_registration(self):
        """Test registration with invalid data"""
        # Test with existing username
        User.objects.create_user(username='existinguser', password='pass123')
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test with mismatched passwords
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test with invalid email
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserProfileViewSetTests(TestCase):
    """Test suite for UserProfile ViewSet"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            name='Test User',
            weight=70.5,
            height=175
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """Test retrieving profile"""
        url = reverse('profile-detail', kwargs={'pk': self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test User')

    def test_update_profile(self):
        """Test updating profile"""
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

    @mock.patch('cloudinary.uploader.upload')
    def test_upload_profile_image(self, mock_upload):
        """Test profile image upload"""
        mock_upload.return_value = {'secure_url': 'http://test-url.com/image.jpg'}
        
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

class GoalTests(TestCase):
    """Test suite for Goals"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.goal = Goal.objects.create(
            user=self.user,
            type='weight',
            description='Lose weight',
            target='80kg',
            deadline=date.today() + timedelta(days=30)
        )

    def test_create_goal(self):
        """Test goal creation"""
        url = reverse('goal-list')
        data = {
            'type': 'strength',
            'description': 'Increase bench press',
            'target': '100kg',
            'deadline': (date.today() + timedelta(days=60)).isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Goal.objects.count(), 2)

    def test_update_goal(self):
        """Test goal update"""
        url = reverse('goal-detail', kwargs={'pk': self.goal.pk})
        data = {
            'target': '75kg',
            'completed': True
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.target, '75kg')
        self.assertTrue(self.goal.completed)

    def test_goal_summary(self):
        """Test goal summary endpoint"""
        url = reverse('goal-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_goals', response.data)
        self.assertIn('completed_goals', response.data)
        self.assertIn('active_goals', response.data)
        self.assertIn('upcoming_deadlines', response.data)

class AuthenticationTests(TestCase):
    """Test suite for authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login(self):
        """Test user login"""
        url = reverse('rest_login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data)

    def test_logout(self):
        """Test user logout"""
        self.client.force_authenticate(user=self.user)
        url = reverse('rest_logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_change(self):
        """Test password change"""
        self.client.force_authenticate(user=self.user)
        url = reverse('rest_password_change')
        data = {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)