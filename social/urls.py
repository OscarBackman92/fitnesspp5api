# social/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'follows', views.UserFollowViewSet, basename='follow')
router.register(r'likes', views.WorkoutLikeViewSet, basename='like')
router.register(r'comments', views.WorkoutCommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('toggle-follow/', 
         views.UserFollowViewSet.as_view({'post': 'toggle_follow'}),
         name='toggle-follow'),
]