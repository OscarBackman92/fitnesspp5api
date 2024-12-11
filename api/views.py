import logging
from django.db.models import Count, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import UserProfile
from .serializers import (
    UserProfileSerializer,
    UserInfoSerializer
)
from config.permissions import IsOwnerOrReadOnly
from django.urls import reverse

logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing user profiles."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, 
                        IsOwnerOrReadOnly]

    def get_queryset(self):
        return UserProfile.objects.select_related('user').prefetch_related('user__workouts').annotate(
        workouts_count=Count('user__workouts', distinct=True)
    ).order_by('-created_at')
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
            'total_workout_time':
                profile.user.workouts.aggregate(total_time=Sum(
                    'duration'))['total_time']
        }
        return Response(stats)

    @action(detail=True, methods=['POST'])
    def upload_image(self, request, pk=None):
        profile = self.get_object()
        image = request.FILES.get('profile_image')
        if image:
            try:
                profile.profile_image = image
                profile.save()
                return Response({"status": "image uploaded successfully"})
            except Exception as e:
                return Response({"error": f"Error during image upload: {str(e)}"}, status=400)
        return Response({"error": "No image provided"}, status=400)

    @action(detail=False, methods=['GET'])
    def full_info(self, request, pk=None):
        """Get full profile information including related data."""
        profile = self.get_object()
        serializer = UserInfoSerializer(profile, context={'request': request})
        return Response(serializer.data)



