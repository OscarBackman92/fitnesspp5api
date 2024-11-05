from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'workouts'

# Set up the DefaultRouter for WorkoutViewSet
router = DefaultRouter()
router.register(r'workouts', views.WorkoutViewSet, basename='workout')

# Define URL patterns with router URLs included
urlpatterns = [
    path('', include(router.urls)),
]
