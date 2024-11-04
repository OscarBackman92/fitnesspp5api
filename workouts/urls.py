from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'workouts'

router = DefaultRouter()
router.register(r'workouts', views.WorkoutViewSet, basename='workout')

urlpatterns = [
    path('', include(router.urls)),
]