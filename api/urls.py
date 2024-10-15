from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, WorkoutViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'workouts', WorkoutViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
