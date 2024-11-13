from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.models import User
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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

class SocialFeedViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['workout__workout_type', 'user__username']
    ordering_fields = ['shared_at', 'likes_count']
    ordering = ['-shared_at']

    def get_queryset(self):
        """
        Get posts from followed users and self.
        Includes options for filtering by timeframe and workout type.
        """
        following = UserFollow.objects.filter(
            follower=self.request.user
        ).values_list('following', flat=True)
        
        queryset = WorkoutPost.objects.filter(
            Q(user=self.request.user) | Q(user__in=following)
        ).select_related(
            'user',
            'workout',
            'user__profile'
        )

        timeframe = self.request.query_params.get('timeframe')
        if timeframe:
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

        workout_type = self.request.query_params.get('workout_type')
        if workout_type:
            queryset = queryset.filter(workout__workout_type=workout_type)

        return queryset.annotate(
            likes_count=Count('workout__likes'),
            comments_count=Count('workout__comments')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['POST'])
    def share_workout(self, request):
        """Share a workout to the social feed."""
        workout_id = request.data.get('workout_id')
        workout = get_object_or_404(Workout, id=workout_id)

        if workout.user != request.user:
            return Response(
                {'error': 'You can only share your own workouts'},
                status=status.HTTP_403_FORBIDDEN
            )

        if WorkoutPost.objects.filter(workout=workout, user=request.user).exists():
            return Response(
                {'error': 'You have already shared this workout'},
                status=status.HTTP_400_BAD_REQUEST
            )

        post = WorkoutPost.objects.create(
            workout=workout,
            user=request.user
        )

        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def toggle_like(self, request, pk=None):
        """Toggle like status for a workout post."""
        post = self.get_object()
        like, created = WorkoutLike.objects.get_or_create(
            user=request.user,
            workout=post.workout
        )

        if not created:
            like.delete()
            return Response({'status': 'unliked'})

        return Response({'status': 'liked'})

    @action(detail=False, methods=['GET'])
    def trending(self, request):
        """Get trending posts based on likes and comments in the last week."""
        week_ago = timezone.now() - timedelta(days=7)
        trending_posts = self.get_queryset().filter(
            shared_at__gte=week_ago
        ).annotate(
            engagement=Count('workout__likes') + Count('workout__comments')
        ).order_by('-engagement')[:5]

        serializer = self.get_serializer(trending_posts, many=True)
        return Response(serializer.data)


class WorkoutCommentViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return WorkoutComment.objects.filter(
            workout_id=self.request.query_params.get('workout_id')
        ).select_related('user', 'user__profile')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """Only allow users to delete their own comments."""
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
        """Toggle follow status for a user."""
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

        serializer = self.get_serializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def suggestions(self, request):
        """Get user suggestions for following based on various factors."""
        following = UserFollow.objects.filter(
            follower=request.user
        ).values_list('following', flat=True)
        
        user_workout_types = Workout.objects.filter(
            user=request.user
        ).values_list('workout_type', flat=True).distinct()
        
        suggested_users = User.objects.exclude(
            Q(id__in=following) | Q(id=request.user.id)
        ).filter(
            workouts__workout_type__in=user_workout_types
        ).annotate(
            workout_count=Count('workouts'),
            follower_count=Count('followers')
        ).order_by('-workout_count', '-follower_count').distinct()[:5]
        
        serializer = UserProfileSerializer(
            suggested_users, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """Get social statistics for the current user."""
        followers_count = UserFollow.objects.filter(following=request.user).count()
        following_count = UserFollow.objects.filter(follower=request.user).count()
        posts_count = WorkoutPost.objects.filter(user=request.user).count()
        
        recent_followers = UserFollow.objects.filter(
            following=request.user
        ).select_related('follower').order_by('-created_at')[:5]
        
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

class WorkoutPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing workout posts in the social feed.
    Supports listing, creating, retrieving, updating, and deleting posts.
    """
    queryset = WorkoutPost.objects.all()
    serializer_class = WorkoutPostSerializer
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        """Override to assign the current user to the post."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def toggle_like(self, request, pk=None):
        """Toggle like status for a workout post."""
        post = self.get_object()
        like, created = WorkoutLike.objects.get_or_create(
            user=request.user,
            workout=post.workout
        )

        if not created:
            like.delete()
            return Response({'status': 'unliked'})

        return Response({'status': 'liked'})

    @action(detail=False, methods=['GET'])
    def trending(self, request):
        """Get trending posts based on likes and comments in the last week."""
        week_ago = timezone.now() - timedelta(days=7)
        trending_posts = self.get_queryset().filter(
            shared_at__gte=week_ago
        ).annotate(
            engagement=Count('workout__likes') + Count('workout__comments')
        ).order_by('-engagement')[:5]

        serializer = self.get_serializer(trending_posts, many=True)
        return Response(serializer.data)