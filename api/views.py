import logging
from django.db.models import Sum, Avg
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserProfile, Workout
from .serializers import UserProfileSerializer, WorkoutSerializer, UserRegistrationSerializer
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            logger.info(f"Workout {instance.id} updated successfully by user {request.user.id}")
            return Response(serializer.data)
        else:
            logger.warning(f"Failed workout update attempt by user {request.user.id}. Errors: {serializer.errors}")
            return Response({
                'status': 'Bad request',
                'message': 'Workout could not be updated with received data.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        try:
            user_workouts = self.get_queryset()
            today = timezone.now().date()
            last_week = today - timezone.timedelta(days=7)
            last_month = today - timezone.timedelta(days=30)

            total_workouts = user_workouts.count()
            total_duration = user_workouts.aggregate(Sum('duration'))['duration__sum'] or 0
            total_calories = user_workouts.aggregate(Sum('calories'))['calories__sum'] or 0
            avg_duration = user_workouts.aggregate(Avg('duration'))['duration__avg'] or 0

            recent_workouts = user_workouts.order_by('-date_logged')[:5]
            workouts_this_week = user_workouts.filter(date_logged__gte=last_week).count()
            workouts_this_month = user_workouts.filter(date_logged__gte=last_month).count()

            return Response({
                'total_workouts': total_workouts,
                'total_duration': total_duration,
                'total_calories': total_calories,
                'avg_duration': avg_duration,
                'recent_workouts': WorkoutSerializer(recent_workouts, many=True).data,
                'workouts_this_week': workouts_this_week,
                'workouts_this_month': workouts_this_month
            })
        except Exception as e:
            logger.error(f"Error generating workout summary for user {request.user.id}: {str(e)}")
            return Response({
                'status': 'Error',
                'message': 'An error occurred while generating the workout summary.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "message": "Please send a POST request to this endpoint with username, email, and password to register.",
            "required_fields": ["username", "email", "password"]
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.info(f"New user registered: {user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            return Response({
                'status': 'Error',
                'message': 'Registration failed. Please check your input and try again.',
                'errors': serializer.errors if hasattr(serializer, 'errors') else str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        return serializer.save()

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