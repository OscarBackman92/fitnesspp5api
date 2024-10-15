from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from .models import UserProfile, Workout
from .serializers import UserProfileSerializer, WorkoutSerializer
from config.permissions import IsAuthenticatedOrReadOnly, IsOwner 


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwner]
        return super().get_permissions()

class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        date = self.request.query_params.get('date_logged')  # Use the correct field name
        if date:
            queryset = queryset.filter(date_logged=date)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
