from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocialFeedViewSet, UserFollowViewSet, WorkoutLikeViewSet, WorkoutCommentViewSet

# Create router instance
router = DefaultRouter()

# Register the viewsets with the correct basename
router.register(r'feed', SocialFeedViewSet, basename='socialfeed')
router.register(r'follow', UserFollowViewSet, basename='userfollow')
router.register(r'likes', WorkoutLikeViewSet, basename='workoutlike')
router.register(r'comments', WorkoutCommentViewSet, basename='workoutcomment')

app_name = 'social'  # Set the app name for URL namespace

# Include router URLs
urlpatterns = [
    path('', include(router.urls)),
    path('feed/share_workout/', SocialFeedViewSet.as_view({'post': 'share_workout'}), name='socialfeed-share_workout'),
]
