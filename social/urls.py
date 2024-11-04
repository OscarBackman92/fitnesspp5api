from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'social'

router = DefaultRouter()
router.register(r'follows', views.UserFollowViewSet, basename='social-follow')
router.register(r'likes', views.WorkoutLikeViewSet, basename='social-like')
router.register(r'comments', views.WorkoutCommentViewSet, basename='social-comment')

urlpatterns = [
    path('', include(router.urls)),
    path('feed/', views.SocialFeedView.as_view(), name='social-feed'),
]