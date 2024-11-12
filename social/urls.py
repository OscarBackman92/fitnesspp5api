from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'social'

router = DefaultRouter()
router.register(r'posts', views.WorkoutPostViewSet, basename='workout-post')
router.register(r'follows', views.UserFollowViewSet, basename='follow')
router.register(r'likes', views.WorkoutLikeViewSet, basename='like')
router.register(r'comments', views.WorkoutCommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('feed/', views.WorkoutPostViewSet.as_view({'get': 'feed'}), name='feed'),
    path('stats/', views.WorkoutPostViewSet.as_view({'get': 'stats'}), name='stats'),
    path('toggle-follow/', views.UserFollowViewSet.as_view({'post': 'toggle_follow'}), name='toggle-follow'),
    path('toggle-like/', views.WorkoutLikeViewSet.as_view({'post': 'toggle'}), name='toggle-like'),
]