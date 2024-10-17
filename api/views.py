from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import UserProfile, Workout
from .serializers import UserProfileSerializer, WorkoutSerializer, UserRegistrationSerializer
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
    search_fields = ['user__username', 'user__email']

    def get_permissions(self):

        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwner]
        return super().get_permissions()

class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        date = self.request.query_params.get('date_logged')
        if date:
            queryset = queryset.filter(date_logged=date)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
