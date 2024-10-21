from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, UserRegistrationView, api_root

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='rest_register'),
]