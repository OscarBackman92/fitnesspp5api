import logging
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserProfile, Goal
from .serializers import (
    UserProfileSerializer,
    GoalSerializer,
    UserRegistrationSerializer,
    UserInfoSerializer
)
from .permissions import IsOwnerOrReadOnly
from django.urls import reverse

logger = logging.getLogger(__name__)

class UserRegistrationView(generics.CreateAPIView):
    """View for user registration."""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                UserProfile.objects.create(user=user)
                return Response({
                    "user": UserRegistrationSerializer(user, context=self.get_serializer_context()).data,
                    "message": "User Created Successfully"
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                return Response({"error": "Could not create user", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for User Profiles."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get queryset with optimized database queries and ordering."""
        return UserProfile.objects.select_related('user').prefetch_related('user__workouts').annotate(
            workouts_count=Count('user__workouts', distinct=True)
        ).order_by('-created_at')  # Order by created_at descending

    def perform_create(self, serializer):
        """Create a new profile."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['GET'])
    def stats(self, request, pk=None):
        """Get user profile statistics for a specific profile."""
        profile = get_object_or_404(UserProfile.objects.annotate(
            workouts_count=Count('user__workouts', distinct=True)
        ), pk=pk)
        
        stats = {
            'total_workouts': profile.user.workouts.count(),
            'workouts_count': profile.workouts_count,
        }
        return Response(stats)

    @action(detail=True, methods=['POST'])
    def upload_image(self, request, pk=None):
        """Upload profile image endpoint."""
        profile = self.get_object()

        if request.user != profile.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if 'profile_image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(profile, data={'profile_image': request.FILES['profile_image']}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def full_info(self, request, pk=None):
        """Get full profile information including related data."""
        profile = self.get_object()
        serializer = UserInfoSerializer(profile, context={'request': request})
        return Response(serializer.data)

class GoalViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing goals."""
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'type']
    filterset_fields = ['type', 'deadline']
    ordering_fields = ['deadline', 'created_at']

    def get_queryset(self):
        queryset = Goal.objects.filter(user_profile__user=self.request.user)
        
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
        serializer.save(user_profile=self.request.user.profile)

    @action(detail=True, methods=['POST'])
    def toggle_completion(self, request, pk=None):
        """Toggle goal completion status."""
        goal = self.get_object()
        goal.completed = not goal.completed
        goal.save()
        serializer = self.get_serializer(goal)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        """Get summary of user's goals."""
        goals = self.get_queryset()
        summary = {
            'total_goals': goals.count(),
            'completed_goals': goals.filter(completed=True).count(),
            'active_goals': goals.filter(completed=False).count(),
            'upcoming_deadlines': goals.filter(completed=False, deadline__gte=timezone.now()).order_by('deadline')[:5].values('description', 'deadline')
        }
        return Response(summary)
