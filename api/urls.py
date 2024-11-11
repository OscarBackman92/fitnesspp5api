# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet,
    GoalViewSet,
    UserRegistrationView,
)
router = DefaultRouter()

router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
]