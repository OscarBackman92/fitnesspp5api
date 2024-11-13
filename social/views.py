from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import WorkoutPost, WorkoutLike, WorkoutComment, UserFollow
from .serializers import (
    WorkoutPostSerializer,
    WorkoutCommentSerializer,
    UserFollowSerializer,
    UserProfileSerializer
)
from workouts.models import Workout

class SocialFeedViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get posts from followed users and self
        """
        following = UserFollow.objects.filter(
            follower=self.request.user
        ).values_list('following', flat=True)
        
        queryset = WorkoutPost.objects.filter(
            Q(user=self.request.user) | Q(user__in=following)
        ).select_related('user', 'workout', 'user__profile')

        # Handle timeframe filter
        timeframe = self.request.query_params.get('timeframe')
        if timeframe and timeframe != 'all':
            if timeframe == 'today':
                queryset = queryset.filter(shared_at__date=timezone.now().date())
            elif timeframe == 'week':
                queryset = queryset.filter(
                    shared_at__gte=timezone.now() - timedelta(days=7)
                )
            elif timeframe == 'month':
                queryset = queryset.filter(
                    shared_at__gte=timezone.now() - timedelta(days=30)
                )

        # Handle workout type filter
        workout_type = self.request.query_params.get('workout_type')
        if workout_type:
            queryset = queryset.filter(workout__workout_type=workout_type)

        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to add error handling"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in SocialFeedViewSet.list: {str(e)}")
            return Response(
                {"error": "Failed to fetch feed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class WorkoutCommentViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        return WorkoutComment.objects.filter(
            workout_id=self.request.query_params.get('workout_id')
        ).select_related('user', 'user__profile')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own comments.")
        instance.delete()

class UserFollowViewSet(viewsets.ModelViewSet):
    serializer_class = UserFollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        filter_type = self.request.query_params.get('type', 'following')
        if filter_type == 'followers':
            return UserFollow.objects.filter(following=self.request.user)
        return UserFollow.objects.filter(follower=self.request.user)

    @action(detail=False, methods=['POST'])
    def toggle_follow(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_to_follow = serializer.validated_data['following_id']
        if user_to_follow == request.user.id:
            return Response(
                {'error': 'You cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow, created = UserFollow.objects.get_or_create(
            follower=request.user,
            following_id=user_to_follow
        )

        if not created:
            follow.delete()
            return Response({'status': 'unfollowed'})

        return Response(self.get_serializer(follow).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        followers_count = UserFollow.objects.filter(following=request.user).count()
        following_count = UserFollow.objects.filter(follower=request.user).count()
        posts_count = WorkoutPost.objects.filter(user=request.user).count()
        
        recent_followers = UserFollow.objects.filter(
            following=request.user
        ).select_related('follower')[:5]
        
        return Response({
            'followers_count': followers_count,
            'following_count': following_count,
            'posts_count': posts_count,
            'recent_followers': UserProfileSerializer(
                [follow.follower for follow in recent_followers],
                many=True,
                context={'request': request}
            ).data
        })