from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'workouts'

router = DefaultRouter()
router.register(r'', views.WorkoutViewSet, basename='workout')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', views.WorkoutViewSet.as_view({'get': 'summary'}), name='workout-summary'),
    path('statistics/', views.WorkoutViewSet.as_view({'get': 'statistics'}), name='workout-statistics'),
]
