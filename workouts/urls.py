from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'workouts'

# Create a router and register the WorkoutViewSet
router = DefaultRouter()
router.register(r'', views.WorkoutViewSet, basename='workout')  # This will handle the list and create endpoints

urlpatterns = [
    path('', include(router.urls)),  # This includes the default routes for list and create
    path('summary/', views.WorkoutViewSet.as_view({'get': 'summary'}), name='workout-summary'),  # Custom summary endpoint
    path('statistics/', views.WorkoutViewSet.as_view({'get': 'statistics'}), name='workout-statistics'),  # Custom statistics endpoint
    path('<int:pk>/', views.WorkoutViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='workout-detail'),  # Detail view for workouts
]
