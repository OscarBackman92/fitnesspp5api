from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from profiles.models import Profile
from profiles.serializers import ProfileSerializer
from profiles.middleware import CustomCommonMiddleware
from django.http import HttpRequest, HttpResponse

class ProfileModelTest(TestCase):
    """Test the Profile model and its related functionality."""

    def setUp(self):
    # Clean up any existing profiles before each test to prevent 4 profiles in the db
        Profile.objects.all().delete()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile, created = Profile.objects.get_or_create(owner=self.user)
        self.client.login(username='testuser', password='password')

    def test_create_profile_on_user_creation(self):
        """Test that a profile is created automatically when a new user is created."""
        user = User.objects.create_user(username='newuser', password='password')
        profile = Profile.objects.get(owner=user)
        self.assertEqual(profile.owner.username, 'newuser')

    def test_profile_string_representation(self):
        """Test the string representation of the Profile model."""
        self.assertEqual(str(self.profile), "testuser's profile")


class ProfileSerializerTest(APITestCase):
    """Test the Profile serializer."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile, created = Profile.objects.get_or_create(owner=self.user)

    def test_profile_serializer(self):
        """Test that the Profile serializer works correctly."""
        # Add the request to the context for serializer to access 'request' for 'is_owner' check
        request = self.client.get('/')  # Creates a valid request object for the context
        serializer = ProfileSerializer(self.profile, context={'request': request})
        self.assertEqual(serializer.data['owner'], self.user.username)
        self.assertEqual(serializer.data['name'], self.profile.name)

    def test_is_owner(self):
        """Test the is_owner field in the Profile serializer."""
        request = self.client.get('/')  # Creates a valid request object for the context
        serializer = ProfileSerializer(self.profile, context={'request': request})
        self.assertTrue(serializer.data['is_owner'])


class ProfileViewTest(APITestCase):
    """Test the Profile views (list and detail)."""

    def setUp(self):
        # Clean up any existing profiles before each test
        Profile.objects.all().delete()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile, created = Profile.objects.get_or_create(owner=self.user)
        self.client.login(username='testuser', password='password')

    def test_profile_list_view(self):
        """Test the profile list view."""
        url = reverse('profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_profile_detail_view(self):
        """Test the profile detail view."""
        url = reverse('profile-detail', kwargs={'pk': self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.profile.name)

    def test_profile_update_view(self):
        """Test the profile update view."""
        url = reverse('profile-detail', kwargs={'pk': self.profile.pk})
        response = self.client.put(url, {'name': 'Updated Profile', 'bio': 'Updated bio'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated Profile')


class ProfileURLsTest(APITestCase):
    """Test the profile URLs."""

    def test_profile_list_url(self):
        """Test that the profile list URL resolves correctly."""
        url = reverse('profile-list')
        self.assertEqual(resolve(url).view_name, 'profile-list')

    def test_profile_detail_url(self):
        """Test that the profile detail URL resolves correctly."""
        url = reverse('profile-detail', kwargs={'pk': 1})
        self.assertEqual(resolve(url).view_name, 'profile-detail')


class MiddlewareTest(TestCase):
    """Test custom middleware functionality."""

    def test_custom_common_middleware(self):
        """Test the custom security headers and request duration."""
        request = HttpRequest()
        response = HttpResponse()
        middleware = CustomCommonMiddleware(get_response=lambda x: response)
        response = middleware.process_response(request, response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
