from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutPostViewSet, CommentViewSet

app_name = 'social'

router = DefaultRouter()
router.register(r'feed', WorkoutPostViewSet, basename='feed')
router.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('feed/<int:pk>/like/', WorkoutPostViewSet.as_view({'post': 'like'}), name='feed-like'),
    path('feed/<int:pk>/comments/', WorkoutPostViewSet.as_view({'post': 'comments'}), name='feed-comments'),
    path('', include(router.urls)),
]
