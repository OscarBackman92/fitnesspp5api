from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet,
    GoalViewSet,
)

router = DefaultRouter()

router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
]
