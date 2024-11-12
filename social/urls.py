from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'feed', views.SocialFeedViewSet, basename='social-feed')
router.register(r'follow', views.UserFollowViewSet, basename='follow')
router.register(r'likes', views.WorkoutLikeViewSet, basename='like')
router.register(r'comments', views.WorkoutCommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]