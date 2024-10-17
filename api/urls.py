from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, WorkoutViewSet, WorkoutSummaryView

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'workouts', WorkoutViewSet, basename='workout')

urlpatterns = [
    path('', include(router.urls)),
    path('workout-summary/', WorkoutSummaryView.as_view(), name='workout-summary'),
]