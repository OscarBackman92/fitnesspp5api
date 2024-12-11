from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from workouts.models import Workout
from django.utils import timezone


class WorkoutTests(APITestCase):
    """Test suite for the Workout API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test users
        self.owner = User.objects.create_user(
            username='owneruser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        # Authenticate the owner user
        self.client.force_authenticate(user=self.owner)

        # Create a test workout for the owner
        self.workout_data = {
            "title": "Morning Run",
            "workout_type": "cardio",
            "duration": 30,
            "intensity": "moderate",
            "notes": "Good pace",
            "date_logged": timezone.now().date().isoformat(),
        }
        self.workout = Workout.objects.create(
            owner=self.owner,
            **self.workout_data
        )

    def test_create_workout(self):
        """Test creating a new workout."""
        new_workout_data = {
            "title": "Evening Yoga",
            "workout_type": "flexibility",
            "duration": 45,
            "intensity": "low",
            "notes": "Relaxing session",
            "date_logged": timezone.now().date().isoformat(),
        }
        response = self.client.post(
            reverse('workouts:workout-list'),
            new_workout_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workout.objects.count(), 2)
        self.assertEqual(response.data['title'], 'Evening Yoga')
        self.assertEqual(response.data['owner'], self.owner.id)

    def test_list_workouts(self):
        """Test listing workouts for the logged-in user."""
        response = self.client.get(reverse('workouts:workout-list'))
        print("Response status code:", response.status_code)
        print("Response data:", response.data)
        print("Workouts owned by owner:", Workout.objects.filter(owner=self.owner))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Check the length of the 'results' list
        self.assertEqual(response.data['results'][0]['title'], 'Morning Run')

    def test_get_workout_detail(self):
        """Test retrieving a specific workout."""
        response = self.client.get(
            reverse('workouts:workout-detail', kwargs={'pk': self.workout.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Morning Run')
        self.assertEqual(response.data['duration'], 30)

    def test_update_workout(self):
        """Test updating a workout."""
        update_data = {
            "title": "Updated Run",
            "duration": 35
        }
        response = self.client.patch(
            reverse('workouts:workout-detail', kwargs={'pk': self.workout.id}),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.workout.refresh_from_db()
        self.assertEqual(self.workout.title, "Updated Run")
        self.assertEqual(self.workout.duration, 35)

    def test_delete_workout(self):
        """Test deleting a workout."""
        response = self.client.delete(
            reverse('workouts:workout-detail', kwargs={'pk': self.workout.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Workout.objects.count(), 0)

    def test_unauthorized_workout_access(self):
        """Test unauthorized access to another user's workout."""
        other_workout = Workout.objects.create(
            owner=self.other_user,
            title="Other's Workout",
            workout_type="strength",
            duration=40,
            intensity="high"
        )
        print("Other workout ID:", other_workout.id)

        # Try to update another user's workout
        response = self.client.patch(
            reverse('workouts:workout-detail', kwargs={'pk': other_workout.id}),
            {"title": "Unauthorized Update"},
            format='json'
        )
        print("Unauthorized update response status code:", response.status_code)
        print("Unauthorized update response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to delete another user's workout
        response = self.client.delete(
            reverse('workouts:workout-detail', kwargs={'pk': other_workout.id})
        )
        print("Unauthorized delete response status code:", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to delete another user's workout
        response = self.client.delete(
            reverse('workouts:workout-detail', kwargs={'pk': other_workout.id})
        )
        print("Unauthorized delete response status code:", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def tearDown(self):
        """Clean up after tests."""
        User.objects.all().delete()
        Workout.objects.all().delete()