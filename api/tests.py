from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import UserProfile, Workout
from datetime import date

class UserRegistrationTestCase(APITestCase):
    def test_user_registration(self):
        url = reverse('rest_register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'profile': {
                'name': 'Test User',
                'weight': 70,
                'height': 175
            }
        }
        response = self.client.post(url, data, format='json')
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)

class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login(self):
        url = reverse('rest_login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.data) 

class UserProfileTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.profile = UserProfile.objects.create(user=self.user, name='Test User', weight=70, height=175)

    def test_get_profile(self):
        url = reverse('profile-detail', kwargs={'pk': self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test User')

    def test_update_profile(self):
        url = reverse('profile-detail', kwargs={'pk': self.profile.pk})
        data = {'name': 'Updated Name', 'weight': 75}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfile.objects.get(pk=self.profile.pk).name, 'Updated Name')

class WorkoutTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)

    def test_create_workout(self):
        url = reverse('workout-list')
        data = {
            'workout_type': 'cardio',
            'duration': 30,
            'calories': 300,
            'date_logged': '2024-10-17'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workout.objects.count(), 1)

    def test_get_workouts(self):
        Workout.objects.create(user=self.user, workout_type='strength', duration=45, calories=200, date_logged=date.today())
        url = reverse('workout-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_workout_summary(self):
        Workout.objects.create(user=self.user, workout_type='cardio', duration=30, calories=300, date_logged=date.today())
        Workout.objects.create(user=self.user, workout_type='strength', duration=45, calories=200, date_logged=date.today())
        url = reverse('workout-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_workouts'], 2)
        self.assertEqual(response.data['total_duration'], 75)
        self.assertEqual(response.data['total_calories'], 500)