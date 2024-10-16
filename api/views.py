from django.db.models import Sum, Avg
from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserProfile, Workout
from .serializers import UserProfileSerializer, WorkoutSerializer, UserRegistrationSerializer
from .permissions import IsOwnerOrReadOnly

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'name']

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['workout_type', 'date_logged']
    search_fields = ['workout_type', 'notes']
    ordering_fields = ['date_logged', 'duration', 'calories']

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        user_workouts = self.get_queryset()
        total_workouts = user_workouts.count()
        total_duration = user_workouts.aggregate(Sum('duration'))['duration__sum'] or 0
        total_calories = user_workouts.aggregate(Sum('calories'))['calories__sum'] or 0
        avg_duration = user_workouts.aggregate(Avg('duration'))['duration__avg'] or 0

        return Response({
            'total_workouts': total_workouts,
            'total_duration': total_duration,
            'total_calories': total_calories,
            'avg_duration': avg_duration
        })

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "message": "Please send a POST request to this endpoint with username, email, password, and profile data to register a new user."
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'profiles': reverse('profile-list', request=request, format=format),
        'workouts': reverse('workout-list', request=request, format=format),
        'register': reverse('rest_register', request=request, format=format),
        'login': reverse('rest_login', request=request, format=format),
        'logout': reverse('rest_logout', request=request, format=format),
        'token': reverse('token_obtain_pair', request=request, format=format),
        'token_refresh': reverse('token_refresh', request=request, format=format),
    })