from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile
from .serializers import UserProfileSerializer, UserRegistrationSerializer, UserInfoSerializer
from datetime import date
from unittest import skip
import json

class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(
            user=self.user,
            name='Test User',
            weight=70,
            height=175,
            date_of_birth=date(1990, 1, 1)
        )

    def test_calculate_bmi(self):
        self.assertAlmostEqual(self.profile.calculate_bmi(), 22.86, places=2)

    def test_age(self):
        today = date.today()
        expected_age = today.year - self.profile.date_of_birth.year
        if today < date(today.year, self.profile.date_of_birth.month, self.profile.date_of_birth.day):
            expected_age -= 1
        self.assertEqual(self.profile.age(), expected_age)

class UserProfileViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user, name='Test User')
        self.client.force_authenticate(user=self.user)

    def test_me_endpoint(self):
        url = reverse('profile-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test User')


class UserRegistrationViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        url = reverse('rest_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
        }
        response = self.client.post(url, data, format='json')
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")
        
        if response.status_code != status.HTTP_201_CREATED:
            try:
                error_data = json.loads(response.content.decode('utf-8'))
                for field, errors in error_data.items():
                    print(f"Errors for {field}: {errors}")
            except json.JSONDecodeError:
                print("Could not parse response content as JSON")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

class SerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(
            user=self.user,
            name='Test User',
            weight=70,
            height=175,
            date_of_birth=date(1990, 1, 1)
        )

    def test_user_profile_serializer(self):
        serializer = UserProfileSerializer(instance=self.profile)
        data = serializer.data
        self.assertEqual(data['name'], 'Test User')
        self.assertIn('bmi', data)
        self.assertIn('age', data)

    def test_user_info_serializer(self):
        serializer = UserInfoSerializer(instance=self.profile)
        data = serializer.data
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['name'], 'Test User')
        self.assertIn('bmi', data)
        self.assertIn('age', data)