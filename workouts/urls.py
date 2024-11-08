from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import WorkoutViewSet

app_name = 'workouts'

router = DefaultRouter()
router.register('', WorkoutViewSet, basename='workout')

# The router will generate these URLs:
# /api/workouts/workouts/ - for list and create
# /api/workouts/workouts/{id}/ - for retrieve, update, delete
# /api/workouts/workouts/statistics/ - for statistics
# /api/workouts/workouts/summary/ - for summary

urlpatterns = router.urls