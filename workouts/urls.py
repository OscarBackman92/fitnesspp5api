from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutViewSet

app_name = 'workouts'

router = DefaultRouter()
router.register('', WorkoutViewSet, basename='workout')

urlpatterns = [
    path('', include(router.urls)),
]
