from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import Workout

class WorkoutViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.force_authenticate(user=self.user)

        # Create a workout for the authenticated user
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
        """Test retrieving all workouts for current user"""
        response = self.client.get(reverse('workouts:workout-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)  # Expecting one workout

    def test_create_workout(self):
        """Test creating a new workout"""
        workout_data = {
            'workout_type': 'strength',
            'date_logged': date.today(),
            'duration': 45,
            'calories': 200,
            'notes': 'New workout',
            'intensity': 'high'
        }
        response = self.client.post(reverse('workouts:workout-list'), workout_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Workout.objects.filter(notes='New workout').exists())

    def test_get_single_workout(self):
        """Test retrieving a single workout"""
        response = self.client.get(reverse('workouts:workout-detail', kwargs={'pk': self.workout.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['duration'], 60)

    def test_update_workout(self):
        """Test updating an existing workout"""
        updated_data = {
            'duration': 75,
            'calories': 400,
            'notes': 'Updated workout'
        }
        response = self.client.patch(reverse('workouts:workout-detail', kwargs={'pk': self.workout.pk}), updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.workout.refresh_from_db()
        self.assertEqual(self.workout.duration, 75)
        self.assertEqual(self.workout.calories, 400)

    def test_delete_workout(self):
        """Test deleting a workout"""
        response = self.client.delete(reverse('workouts:workout-detail', kwargs={'pk': self.workout.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Workout.objects.filter(pk=self.workout.pk).exists())

    def test_workout_filtering(self):
        """Test workout filtering options"""
        start_date = (date.today() - timedelta(days=2)).isoformat()
        response = self.client.get(reverse('workouts:workout-list'), {'start_date': start_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create another workout for the same user
        Workout.objects.create(
            user=self.user,
            workout_type='cardio',
            date_logged=date.today() - timedelta(days=1),
            duration=30,
            calories=150,
            notes='Previous workout',
            intensity='low'
        )

        # Check that both workouts are retrieved
        response = self.client.get(reverse('workouts:workout-list'))
        self.assertEqual(len(response.data['results']), 2)  # Now two workouts

    def test_workout_ordering(self):
        """Test workout ordering options"""
        response = self.client.get(reverse('workouts:workout-list'), {'ordering': '-date_logged'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['date_logged'], date.today().isoformat())

    def test_workout_summary(self):
        """Test workout summary functionality"""
        response = self.client.get(reverse('workouts:workout-summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['total_workouts'], 1)
        self.assertEqual(response.data['total_duration'], 60)
        self.assertEqual(response.data['total_calories'], 300)
        self.assertEqual(round(response.data['avg_duration']), 60)

    def test_workout_statistics(self):
        """Test workout statistics functionality"""
        response = self.client.get(reverse('workouts:workout-statistics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('workout_types', response.data)
        self.assertIn('monthly_trends', response.data)
        self.assertIn('intensity_distribution', response.data)
        self.assertIn('streaks', response.data)

    def test_summary_with_no_workouts(self):
        """Test workout summary functionality with no workouts"""
        self.client.force_authenticate(user=self.other_user)  # Switch user
        response = self.client.get(reverse('workouts:workout-summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_workouts'], 0)
        self.assertEqual(response.data['total_duration'], 0)
        self.assertEqual(response.data['total_calories'], 0)
        self.assertEqual(response.data['avg_duration'], 0)


    def test_permission_handling(self):
        """Test permission handling for workouts"""
        self.client.force_authenticate(user=self.other_user)  # Switch user
        response = self.client.patch(
            reverse('workouts:workout-detail', kwargs={'pk': self.workout.pk}),
            {'duration': 90}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            reverse('workouts:workout-detail', kwargs={'pk': self.workout.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_data_handling(self):
        """Test handling of invalid data"""
        response = self.client.post(
            reverse('workouts:workout-list'),
            {
                'workout_type': 'cardio',
                'duration': -30,
                'calories': 200
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            reverse('workouts:workout-list'),
            {
                'workout_type': 'cardio',
                'duration': 30,
                'calories': 200,
                'intensity': 'invalid'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
