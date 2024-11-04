import logging
import traceback
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserProfile, Goal
from django.urls import reverse
from .serializers import (
    UserProfileSerializer, 
    GoalSerializer, 
    UserRegistrationSerializer,
    UserInfoSerializer
)
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root view showing available endpoints
    """
    return Response({
        'profiles': reverse('profile-list', request=request, format=format),
        'goals': reverse('goal-list', request=request, format=format),
    })

class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({
                    "user": UserRegistrationSerializer(
                        user, 
                        context=self.get_serializer_context()
                    ).data,
                    "message": "User Created Successfully"
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                return Response({
                    "error": "Could not create user",
                    "details": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing user profiles
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ['user__username', 'name']
    filterset_fields = ['gender']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        """
        Get queryset with optimized database queries
        """
        queryset = UserProfile.objects.select_related('user').prefetch_related(
            'user__workouts',
            'user__goals'
        ).annotate(
            workouts_count=Count('user__workouts', distinct=True),
            avg_workout_duration=Avg('user__workouts__duration'),
            total_calories=Sum('user__workouts__calories')
        )

        search_query = self.request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(name__icontains=search_query)
            )

        return queryset

    def perform_create(self, serializer):
        """Create a new profile"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """
        Get user profile statistics
        """
        profile = get_object_or_404(UserProfile, user=request.user)
        stats = {
            'total_workouts': profile.user.workouts.count(),
            'total_calories': profile.user.workouts.aggregate(
                total=Sum('calories')
            )['total'] or 0,
            'avg_duration': profile.user.workouts.aggregate(
                avg=Avg('duration')
            )['avg'] or 0,
        }
        return Response(stats)

    @action(detail=True, methods=['POST'])
    def upload_image(self, request, pk=None):
        """Upload profile image endpoint"""
        profile = self.get_object()
        
        if 'profile_image' not in request.FILES:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            profile,
            data={'profile_image': request.FILES['profile_image']},
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_update(self, serializer):
        """Handle profile update including image upload"""
        instance = serializer.instance
        if 'profile_image' in self.request.FILES:
            old_image = None
            if instance.profile_image:
                old_image = instance.profile_image

            instance = serializer.save()

            if old_image and 'default_profile_image' not in str(old_image):
                try:
                    old_image.delete()
                except Exception as e:
                    logger.error(f"Error deleting old profile image: {e}")
        else:
            serializer.save()

    @action(detail=True, methods=['GET'])
    def full_info(self, request, pk=None):
        """
        Get full profile information including related data
        """
        profile = self.get_object()
        serializer = UserInfoSerializer(profile, context={'request': request})
        return Response(serializer.data)

class GoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing goals
    """
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'type']
    filterset_fields = ['type', 'deadline']
    ordering_fields = ['deadline', 'created_at']

    def get_queryset(self):
        queryset = Goal.objects.filter(user=self.request.user)
        
        status = self.request.query_params.get('status', None)
        if status:
            if status == 'completed':
                queryset = queryset.filter(completed=True)
            elif status == 'active':
                queryset = queryset.filter(completed=False)

        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(deadline__range=[start_date, end_date])

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def toggle_completion(self, request, pk=None):
        """
        Toggle goal completion status
        """
        goal = self.get_object()
        goal.completed = not goal.completed
        goal.save()
        serializer = self.get_serializer(goal)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        """
        Get summary of user's goals
        """
        goals = self.get_queryset()
        summary = {
            'total_goals': goals.count(),
            'completed_goals': goals.filter(completed=True).count(),
            'active_goals': goals.filter(completed=False).count(),
            'upcoming_deadlines': goals.filter(
                completed=False,
                deadline__gte=timezone.now()
            ).order_by('deadline')[:5].values('description', 'deadline')
        }
        return Response(summary)

@api_view(['GET'])
def api_root(request):
    """
    API root view providing links to all main endpoints
    """
    return Response({
        'profiles': f"{request.build_absolute_uri('/api/profiles/')}",
        'goals': f"{request.build_absolute_uri('/api/goals/')}",
        'auth': {
            'login': f"{request.build_absolute_uri('/api/auth/login/')}",
            'logout': f"{request.build_absolute_uri('/api/auth/logout/')}",
            'register': f"{request.build_absolute_uri('/api/auth/registration/')}",
        },
        'workouts': f"{request.build_absolute_uri('/api/workouts/')}",
        'social': {
            'feed': f"{request.build_absolute_uri('/api/feed/')}",
            'follows': f"{request.build_absolute_uri('/api/follows/')}",
            'likes': f"{request.build_absolute_uri('/api/likes/')}",
            'comments': f"{request.build_absolute_uri('/api/comments/')}",
        },
        'documentation': {
            'swagger': f"{request.build_absolute_uri('/swagger/')}",
            'redoc': f"{request.build_absolute_uri('/redoc/')}",
        }
    })