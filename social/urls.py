from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'social'

router = DefaultRouter()
router.register(r'feed', views.SocialFeedViewSet, basename='socialfeed')
router.register(r'follow', views.UserFollowViewSet, basename='userfollow')
router.register(r'likes', views.WorkoutLikeViewSet, basename='workoutlike')
router.register(r'comments', views.WorkoutCommentViewSet, basename='workoutcomment')

urlpatterns = [
    path('', include(router.urls)),
    path('feed/share_workout/', 
         views.SocialFeedViewSet.as_view({'post': 'share_workout'}),
         name='socialfeed-share_workout'),
    path('stats/',
         views.SocialFeedViewSet.as_view({'get': 'stats'}),
         name='social-stats'),
    path('follow/toggle/',
         views.UserFollowViewSet.as_view({'post': 'toggle_follow'}),
         name='userfollow-toggle-follow'),
]