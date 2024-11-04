# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'goals', views.GoalViewSet, basename='goal')

urlpatterns = [
    # API root view
    path('', views.api_root, name='api-root'),
    
    # Router generated URLs
    path('', include(router.urls)),
]