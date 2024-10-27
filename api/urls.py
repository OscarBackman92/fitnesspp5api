from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    UserProfileViewSet,
    GoalViewSet,
    MeasurementViewSet,
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'measurements', MeasurementViewSet, basename='measurement')

urlpatterns = router.urls