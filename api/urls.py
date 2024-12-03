from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, GoalViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
    # Explicitly define the upload_image route for POST requests
    path('profiles/<int:pk>/upload_image/', 
         UserProfileViewSet.as_view({'post': 'upload_image'}), 
         name='profile-upload-image'),
]
