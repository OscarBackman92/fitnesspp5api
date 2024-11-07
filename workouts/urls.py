from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'workouts'

router = DefaultRouter()
router.register(r'', views.WorkoutViewSet, basename='workout')

# Add any additional routes on top of the router URLs
urlpatterns = [
    path('', include(router.urls)),
]