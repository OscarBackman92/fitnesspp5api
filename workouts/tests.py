from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Workout


class WorkoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.workout_data = {
            'title': 'Morning Run',
            'workout_type': 'cardio',
            'duration': 30,
            'description': '5k run'
        }

    def test_can_create_workout(self):
        response = self.client.post('/workouts/', self.workout_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workout.objects.count(), 1)
        self.assertEqual(Workout.objects.get().title, 'Morning Run')

    def test_user_can_list_own_workouts(self):
        Workout.objects.create(owner=self.user, **self.workout_data)
        response = self.client.get('/workouts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_user_can_update_own_workout(self):
        workout = Workout.objects.create(owner=self.user, **self.workout_data)
        updated_data = {
            'title': 'Updated Run',
            'workout_type': 'cardio',
            'duration': 30,
            'description': '5k run'
        }
        response = self.client.put(
            f'/workouts/{workout.id}/',
            updated_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workout.refresh_from_db()
        self.assertEqual(workout.title, 'Updated Run')

    def test_user_cant_update_another_users_workout(self):
        other_user = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        workout = Workout.objects.create(owner=other_user, **self.workout_data)
        response = self.client.put(
            f'/workouts/{workout.id}/',
            {'title': 'Updated Run', **self.workout_data}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
