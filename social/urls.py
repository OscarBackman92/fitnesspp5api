from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserFollowViewSet, WorkoutLikeViewSet, WorkoutCommentViewSet

router = DefaultRouter()
router.register(r'follow', UserFollowViewSet, basename='userfollow')
router.register(r'likes', WorkoutLikeViewSet, basename='workoutlike')
router.register(r'comments', WorkoutCommentViewSet, basename='workoutcomment')

urlpatterns = [
    path('', include(router.urls)),
]
