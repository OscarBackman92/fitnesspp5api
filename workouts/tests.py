from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.utils import timezone
from workouts.models import Workout
from datetime import datetime, timedelta

class WorkoutViewSetTests(APITestCase):
    def setUp(self):
        """Set up test data."""
        # Clean up any existing data
        Workout.objects.all().delete()
        User.objects.all().delete()
            
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            email='other@example.com'
        )
        
        self.client.force_authenticate(user=self.user)
        
        self.workout_data = {
            'workout_type': 'cardio',
            'date_logged': timezone.now().date().isoformat(),
            'duration': 30,
            'notes': 'Test workout',
            'intensity': 'moderate'
        }

        # Define the base API path
        self.base_url = '/api/workouts/workouts/'

    def tearDown(self):
        """Clean up after each test."""
        Workout.objects.all().delete()
        User.objects.all().delete()

    def test_create_workout(self):
        """Test creating a new workout."""
        response = self.client.post(self.base_url, self.workout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['workout_type'], 'cardio')
        self.assertEqual(response.data['duration'], 30)

    def test_retrieve_workout(self):
        """Test retrieving a specific workout."""
        workout = Workout.objects.create(user=self.user, **self.workout_data)
        response = self.client.get(f'{self.base_url}{workout.id}/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], workout.id)
        self.assertEqual(response.data['workout_type'], workout.workout_type)

    def test_update_workout(self):
        """Test updating a workout."""
        workout = Workout.objects.create(user=self.user, **self.workout_data)
        updated_data = {
            **self.workout_data,
            'duration': 45,
            'notes': 'Updated workout'
        }
        
        response = self.client.put(f'{self.base_url}{workout.id}/', updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workout.refresh_from_db()
        self.assertEqual(workout.duration, 45)
        self.assertEqual(workout.notes, 'Updated workout')

    def test_delete_workout(self):
        """Test deleting a workout."""
        workout = Workout.objects.create(user=self.user, **self.workout_data)
        response = self.client.delete(f'{self.base_url}{workout.id}/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Workout.objects.count(), 0)

    def test_workout_statistics(self):
        """Test workout statistics endpoint."""
        workout = Workout.objects.create(user=self.user, **self.workout_data)
        response = self.client.get(f'{self.base_url}statistics/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('workout_types', response.data)
        self.assertIn('monthly_trends', response.data)
        self.assertIn('intensity_distribution', response.data)
        self.assertIn('streaks', response.data)

    def test_workout_summary(self):
        """Test workout summary endpoint."""
        workout = Workout.objects.create(user=self.user, **self.workout_data)
        response = self.client.get(f'{self.base_url}summary/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_workouts', response.data)
        self.assertIn('total_duration', response.data)
        self.assertIn('avg_duration', response.data)
        self.assertIn('recent_workouts', response.data)

    def test_unauthorized_access(self):
        """Test unauthorized access to workouts."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.base_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_other_user_workout(self):
        """Test accessing another user's workout."""
        other_workout = Workout.objects.create(
            user=self.other_user,
            **self.workout_data
        )
        response = self.client.get(f'{self.base_url}{other_workout.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_workout_data(self):
        """Test creating workout with invalid data."""
        invalid_data = {
            **self.workout_data,
            'duration': -1  # Invalid duration
        }
        response = self.client.post(self.base_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('duration', response.data)