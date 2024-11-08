from django.urls import path
from .views import WorkoutViewSet
from social.views import WorkoutCommentViewSet, WorkoutLikeViewSet

app_name = 'workouts'

urlpatterns = [
    path('workouts/', WorkoutViewSet.as_view({'get': 'list', 'post': 'create'}), name='workout-list'),
    path('workouts/<int:pk>/', WorkoutViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='workout-detail'),
    path('workouts/<int:workout_id>/comments/', WorkoutCommentViewSet.as_view({'post': 'create'}), name='workout-comment'),
    path('workouts/<int:workout_id>/likes/', WorkoutLikeViewSet.as_view({'post': 'create'}), name='workout-like'),
]
