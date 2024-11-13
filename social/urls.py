from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutPostViewSet, CommentViewSet

app_name = 'social'

router = DefaultRouter()
router.register(r'feed', WorkoutPostViewSet, basename='feed')
router.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
]