from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]