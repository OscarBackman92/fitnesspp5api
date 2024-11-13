from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocialFeedViewSet, WorkoutCommentViewSet, UserFollowViewSet

app_name = 'social'

router = DefaultRouter()
router.register(r'feed', SocialFeedViewSet, basename='social-feed')
router.register(r'comments', WorkoutCommentViewSet, basename='comments')
router.register(r'follows', UserFollowViewSet, basename='follows')

urlpatterns = [
    path('', include(router.urls)),
    # Add explicit path for stats
    path('follows/stats/', 
         UserFollowViewSet.as_view({'get': 'stats'}), 
         name='stats'),
]