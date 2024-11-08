from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from workouts.models import Workout, WorkoutComment, WorkoutLike
from workouts.serializers import WorkoutSerializer, WorkoutCommentSerializer, WorkoutLikeSerializer

class WorkoutViewSetTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.workout_data = {
            'workout_type': 'cardio',
            'date_logged': '2024-01-01',
            'duration': 30,
            'notes': 'Ran 5km',
            'intensity': 'moderate'
        }

    def test_create_workout(self):
        response = self.client.post(reverse('workouts:workout-list'), self.workout_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workout.objects.count(), 1)

    def test_update_workout(self):
        workout = Workout.objects.create(user=self.user, **self.workout_data)
        update_data = {'duration': 45}
        response = self.client.put(reverse('workouts:workout-detail', args=[workout.id]), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workout.refresh_from_db()
        self.assertEqual(workout.duration, 45)

    def test_delete_workout(self):
        workout = Workout.objects.create(user=self.user, **self.workout_data)
        response = self.client.delete(reverse('workouts:workout-detail', args=[workout.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Workout.objects.count(), 0)

    def test_list_workouts(self):
        Workout.objects.create(user=self.user, **self.workout_data)
        response = self.client.get(reverse('workouts:workout-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_workout_detail(self):
        workout = Workout.objects.create(user=self.user, **self.workout_data)
        response = self.client.get(reverse('workouts:workout-detail', args=[workout.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['workout_type'], workout.workout_type)

class WorkoutCommentViewSetTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.workout_data = {
            'workout_type': 'cardio',
            'date_logged': '2024-01-01',
            'duration': 30,
            'notes': 'Ran 5km',
            'intensity': 'moderate'
        }
        self.workout = Workout.objects.create(user=self.user, **self.workout_data)
        self.comment_data = {'content': 'Great workout!', 'workout': self.workout.id}

    def test_create_comment(self):
        response = self.client.post(reverse('workouts:workout-comment', args=[self.workout.id]), self.comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutComment.objects.count(), 1)

    def test_get_comments(self):
        self.client.post(reverse('workouts:workout-comment', args=[self.workout.id]), self.comment_data)
        response = self.client.get(reverse('workouts:workout-comment', args=[self.workout.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_comment(self):
        comment = WorkoutComment.objects.create(user=self.user, workout=self.workout, content='Nice run!')
        response = self.client.delete(reverse('workouts:workoutcomment-detail', args=[comment.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(WorkoutComment.objects.count(), 0)
class WorkoutLikeViewSetTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.workout_data = {
            'workout_type': 'cardio',
            'date_logged': '2024-01-01',
            'duration': 30,
            'notes': 'Ran 5km',
            'intensity': 'moderate'
        }
        self.workout = Workout.objects.create(user=self.user, **self.workout_data)

    def test_like_workout(self):
        response = self.client.post(reverse('workouts:workout-like', args=[self.workout.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unlike_workout(self):
        self.client.post(reverse('workouts:workout-like', args=[self.workout.id]))
        response = self.client.delete(reverse('workouts:workout-like', args=[self.workout.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
