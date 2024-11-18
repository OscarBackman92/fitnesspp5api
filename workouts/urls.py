from django.urls import path
from workouts import views

urlpatterns = [
    path('workouts/', views.WorkoutList.as_view()),
    path('workouts/<int:pk>/', views.WorkoutDetail.as_view()),
    path('comments/', views.WorkoutCommentList.as_view()),
    path('comments/<int:pk>/', views.WorkoutCommentDetail.as_view()),
]