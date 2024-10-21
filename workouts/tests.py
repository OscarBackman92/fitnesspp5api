from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import Workout
from .serializers import WorkoutSerializer

class WorkoutModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.workout = Workout.objects.create(
            user=self.user,
            workout_type='cardio',
            date_logged=date.today(),
            duration=60,
            calories=300,
            notes='Test workout',
            intensity='moderate'
        )

    def test_workout_creation(self):
        self.assertTrue(isinstance(self.workout, Workout))
        self.assertEqual(self.workout.__str__(), f"{self.user.username} - Cardio on {date.today()}")

    def test_get_duration_in_hours(self):
        self.assertEqual(self.workout.get_duration_in_hours(), 1.0)

class WorkoutSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.workout_data = {
            'workout_type': 'strength',
            'date_logged': date.today(),
            'duration': 45,
            'calories': 200,
            'notes': 'Test strength workout',
            'intensity': 'high'
        }
        self.serializer = WorkoutSerializer(data=self.workout_data)

    def test_serializer_with_valid_data(self):
        self.assertTrue(self.serializer.is_valid())

    def test_serializer_with_invalid_data(self):
        invalid_data = self.workout_data.copy()
        invalid_data['duration'] = 1500  # More than 24 hours
        serializer = WorkoutSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

class WorkoutViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.workout = Workout.objects.create(
            user=self.user,
            workout_type='cardio',
            date_logged=date.today(),
            duration=60,
            calories=300,
            notes='Test workout',
            intensity='moderate'
        )

    def test_get_all_workouts(self):
        response = self.client.get(reverse('workout-list'))
        workouts = Workout.objects.filter(user=self.user)
        serializer = WorkoutSerializer(workouts, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_workout(self):
        workout_data = {
            'workout_type': 'strength',
            'date_logged': date.today(),
            'duration': 45,
            'calories': 200,
            'notes': 'New workout',
            'intensity': 'high'
        }
        response = self.client.post(reverse('workout-list'), workout_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_valid_single_workout(self):
        response = self.client.get(reverse('workout-detail', kwargs={'pk': self.workout.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_workout(self):
        response = self.client.get(reverse('workout-detail', kwargs={'pk': 30}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_workout(self):
        updated_data = {
            'workout_type': 'flexibility',
            'duration': 30,
            'calories': 100,
        }
        response = self.client.patch(reverse('workout-detail', kwargs={'pk': self.workout.pk}), updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_workout(self):
        response = self.client.delete(reverse('workout-detail', kwargs={'pk': self.workout.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_workout_summary(self):
        response = self.client.get(reverse('workout-summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_workouts', response.data)
        self.assertIn('total_duration', response.data)
        self.assertIn('total_calories', response.data)
        self.assertIn('avg_duration', response.data)
        self.assertIn('recent_workouts', response.data)
        self.assertIn('workouts_this_week', response.data)
        self.assertIn('workouts_this_month', response.data)

    def test_filter_workouts(self):
        response = self.client.get(reverse('workout-list'), {'workout_type': 'cardio'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_workouts(self):
        response = self.client.get(reverse('workout-list'), {'search': 'Test workout'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_order_workouts(self):
        Workout.objects.create(
            user=self.user,
            workout_type='strength',
            date_logged=date.today() - timedelta(days=1),
            duration=45,
            calories=200,
        )
        response = self.client.get(reverse('workout-list'), {'ordering': '-date_logged'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['workout_type'], 'cardio')