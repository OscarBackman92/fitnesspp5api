# tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import Workout
from .serializers import WorkoutSerializer

class WorkoutModelTests(TestCase):
    """Test suite for the Workout model"""
    
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
        """Test the workout model creation and string representation"""
        self.assertTrue(isinstance(self.workout, Workout))
        self.assertEqual(
            self.workout.__str__(), 
            f"{self.user.username} - Cardio (moderate) on {date.today()}"
        )

    def test_get_duration_in_hours(self):
        """Test the duration conversion to hours"""
        self.assertEqual(self.workout.get_duration_in_hours(), 1.0)

    def test_workout_defaults(self):
        """Test the default values when creating a workout"""
        minimal_workout = Workout.objects.create(
            user=self.user,
            workout_type='cardio',
            duration=30,
            calories=150
        )
        self.assertEqual(minimal_workout.intensity, 'moderate')
        self.assertEqual(minimal_workout.date_logged, date.today())
        self.assertEqual(minimal_workout.notes, '')

class WorkoutViewSetTests(TestCase):
    """Test suite for the WorkoutViewSet"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.force_authenticate(user=self.user)
        
        # Create test workouts
        self.workout = Workout.objects.create(
            user=self.user,
            workout_type='cardio',
            date_logged=date.today(),
            duration=60,
            calories=300,
            notes='Test workout',
            intensity='moderate'
        )
        
        self.yesterday_workout = Workout.objects.create(
            user=self.user,
            workout_type='strength',
            date_logged=date.today() - timedelta(days=1),
            duration=45,
            calories=200,
            intensity='high'
        )

        self.last_week_workout = Workout.objects.create(
            user=self.user,
            workout_type='flexibility',
            date_logged=date.today() - timedelta(days=7),
            duration=30,
            calories=100,
            intensity='low'
        )

        self.other_user_workout = Workout.objects.create(
            user=self.other_user,
            workout_type='cardio',
            date_logged=date.today(),
            duration=60,
            calories=300,
            intensity='moderate'
        )

    def test_get_all_workouts(self):
        """Test retrieving all workouts for current user"""
        response = self.client.get(reverse('workout-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 3)

        workouts = Workout.objects.filter(user=self.user)
        serializer = WorkoutSerializer(workouts, many=True)
        self.assertEqual(response.data['results'], serializer.data)

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
        response = self.client.post(reverse('workout-list'), workout_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Workout.objects.filter(notes='New workout').exists())

    def test_get_single_workout(self):
        """Test retrieving a single workout"""
        response = self.client.get(
            reverse('workout-detail', kwargs={'pk': self.workout.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['duration'], 60)

    def test_update_workout(self):
        """Test updating an existing workout"""
        updated_data = {
            'duration': 75,
            'calories': 400,
            'notes': 'Updated workout'
        }
        response = self.client.patch(
            reverse('workout-detail', kwargs={'pk': self.workout.pk}),
            updated_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.workout.refresh_from_db()
        self.assertEqual(self.workout.duration, 75)
        self.assertEqual(self.workout.calories, 400)

    def test_delete_workout(self):
        """Test deleting a workout"""
        response = self.client.delete(
            reverse('workout-detail', kwargs={'pk': self.workout.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Workout.objects.filter(pk=self.workout.pk).exists())

    def test_workout_filtering(self):
        """Test workout filtering options"""
        # Test date range filtering
        start_date = (date.today() - timedelta(days=2)).isoformat()
        response = self.client.get(
            reverse('workout-list'),
            {'start_date': start_date}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        # Test workout type filtering
        response = self.client.get(
            reverse('workout-list'),
            {'workout_type': 'cardio'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['workout_type'], 'cardio')

        # Test intensity filtering
        response = self.client.get(
            reverse('workout-list'),
            {'intensity': 'high'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['intensity'], 'high')

    def test_workout_ordering(self):
        """Test workout ordering options"""
        # Test date ordering
        response = self.client.get(
            reverse('workout-list'),
            {'ordering': '-date_logged'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['date_logged'],
            date.today().isoformat()
        )

        # Test duration ordering
        response = self.client.get(
            reverse('workout-list'),
            {'ordering': '-duration'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['duration'], 60)

    def test_workout_summary(self):
        """Test workout summary functionality"""
        response = self.client.get(reverse('workout-summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data['total_workouts'], 3)
        self.assertEqual(response.data['total_duration'], 135)
        self.assertEqual(response.data['total_calories'], 600)
        self.assertEqual(round(response.data['avg_duration']), 45)

    def test_workout_statistics(self):
        """Test workout statistics functionality"""
        response = self.client.get(reverse('workout-statistics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn('workout_types', response.data)
        self.assertIn('monthly_trends', response.data)
        self.assertIn('intensity_distribution', response.data)
        self.assertIn('streaks', response.data)

        # Verify workout types
        workout_types = response.data['workout_types']
        self.assertTrue(isinstance(workout_types, list))
        
        # Verify intensities
        intensity_dist = response.data['intensity_distribution']
        intensities = {i['intensity'] for i in intensity_dist}
        self.assertTrue({'low', 'moderate', 'high'}.issubset(intensities))

    def test_permission_handling(self):
        """Test permission handling for workouts"""
        # Try to update other user's workout
        response = self.client.patch(
            reverse('workout-detail', kwargs={'pk': self.other_user_workout.pk}),
            {'duration': 90}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to delete other user's workout
        response = self.client.delete(
            reverse('workout-detail', kwargs={'pk': self.other_user_workout.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_data_handling(self):
        """Test handling of invalid data"""
        # Test invalid duration
        response = self.client.post(
            reverse('workout-list'),
            {
                'workout_type': 'cardio',
                'duration': -30,
                'calories': 200
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid intensity
        response = self.client.post(
            reverse('workout-list'),
            {
                'workout_type': 'cardio',
                'duration': 30,
                'calories': 200,
                'intensity': 'invalid'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)