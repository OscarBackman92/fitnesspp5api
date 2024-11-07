from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'goals', views.GoalViewSet, basename='goal')

urlpatterns = [
    path('', views.api_root, name='api-root'),  # Root API endpoint
    path('', include(router.urls)),  # Include the router URLs
]
