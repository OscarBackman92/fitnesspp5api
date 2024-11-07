from django.urls import path, include
from .views import UserFollowViewSet, WorkoutLikeViewSet, WorkoutCommentViewSet  # Ensure you import your views
from workouts.views import WorkoutViewSet  # Import WorkoutViewSet from workouts

urlpatterns = [
    path('toggle-follow/', UserFollowViewSet.as_view({'post': 'toggle_follow'}), name='toggle-follow'),
    path('follows/', UserFollowViewSet.as_view({'get': 'list', 'post': 'create'}), name='follow-list'),
    path('likes/', WorkoutLikeViewSet.as_view({'get': 'list', 'post': 'create'}), name='like-list'),
    path('comments/', WorkoutCommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='comment-list'),
    path('feed/', UserFollowViewSet.as_view({'get': 'get_feed'}), name='feed'),
    path('followers-count/', UserFollowViewSet.as_view({'get': 'followers_count'}), name='followers-count'),
    path('following-count/', UserFollowViewSet.as_view({'get': 'following_count'}), name='following-count'),
    path('comments/<int:pk>/', WorkoutCommentViewSet.as_view({'delete': 'destroy'}), name='comment-detail'),
    path('workouts/<int:pk>/', WorkoutViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='workout-detail'),  # Ensure this view exists
]
