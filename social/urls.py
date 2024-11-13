from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocialFeedViewSet, WorkoutPostViewSet, WorkoutCommentViewSet, UserFollowViewSet

app_name = 'social'

router = DefaultRouter()
router.register(r'feed', SocialFeedViewSet, basename='social-feed')
router.register(r'posts', WorkoutPostViewSet, basename='workout-post')  # Register WorkoutPostViewSet
router.register(r'comments', WorkoutCommentViewSet, basename='comment')
router.register(r'follows', UserFollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
]
