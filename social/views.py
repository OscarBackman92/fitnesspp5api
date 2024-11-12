from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import UserFollow, WorkoutLike, WorkoutComment, WorkoutPost, Workout
from .serializers import (
    UserFollowSerializer,
    WorkoutLikeSerializer,
    WorkoutCommentSerializer,
    WorkoutPostSerializer
)
from api.permissions import IsOwnerOrReadOnly

class WorkoutPostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = WorkoutPostSerializer
    filterset_fields = ['user']
    search_fields = ['caption']
    ordering_fields = ['shared_at']

    def get_queryset(self):
        return WorkoutPost.objects.filter(
            Q(user=self.request.user) |
            Q(user__in=UserFollow.objects.filter(
                follower=self.request.user
            ).values_list('following', flat=True))
        ).select_related('user', 'workout').annotate(
            likes_count=Count('workout_likes', distinct=True),
            comments_count=Count('workout_comments', distinct=True)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def feed(self, request):
        """Get social feed of workouts from followed users"""
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        start = (page - 1) * limit
        end = start + limit

        queryset = self.get_queryset().order_by('-shared_at')[start:end]
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'results': serializer.data,
            'next': page + 1 if end < self.get_queryset().count() else None,
            'count': self.get_queryset().count()
        })

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """Get social statistics for the current user or specified user"""
        user_id = request.query_params.get('user_id', request.user.id)
        target_user = get_object_or_404(User, id=user_id)

        # Basic stats
        followers_count = UserFollow.objects.filter(following=target_user).count()
        following_count = UserFollow.objects.filter(follower=target_user).count()
        posts_count = WorkoutPost.objects.filter(user=target_user).count()

        # Recent activity
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_posts = WorkoutPost.objects.filter(
            user=target_user,
            shared_at__gte=thirty_days_ago
        )
        recent_likes = WorkoutLike.objects.filter(
            workout__user=target_user,
            created_at__gte=thirty_days_ago
        ).count()
        recent_comments = WorkoutComment.objects.filter(
            workout__user=target_user,
            created_at__gte=thirty_days_ago
        ).count()

        # Engagement rate
        engagement_rate = 0
        if posts_count > 0:
            total_engagement = recent_likes + recent_comments
            engagement_rate = round((total_engagement / posts_count) * 100, 2)

        return Response({
            'user_id': target_user.id,
            'username': target_user.username,
            'followers_count': followers_count,
            'following_count': following_count,
            'posts_count': posts_count,
            'recent_activity': {
                'posts': recent_posts.count(),
                'likes_received': recent_likes,
                'comments_received': recent_comments,
                'engagement_rate': engagement_rate
            },
            'is_following': UserFollow.objects.filter(
                follower=request.user,
                following=target_user
            ).exists() if request.user != target_user else None
        })

class UserFollowViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserFollowSerializer
    
    def get_queryset(self):
        return UserFollow.objects.filter(
            Q(follower=self.request.user) | Q(following=self.request.user)
        )

    @action(detail=False, methods=['POST'])
    def toggle_follow(self, request):
        user_to_follow = get_object_or_404(User, id=request.data.get('user_id'))
        
        if user_to_follow == request.user:
            return Response(
                {'error': 'Cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow, created = UserFollow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            follow.delete()
            return Response({'status': 'unfollowed'})

        serializer = self.get_serializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class WorkoutLikeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = WorkoutLikeSerializer

    def get_queryset(self):
        return WorkoutLike.objects.filter(user=self.request.user)

    @action(detail=False, methods=['POST'])
    def toggle(self, request):
        workout_id = request.data.get('workout_id')
        workout = get_object_or_404(Workout, id=workout_id)

        like, created = WorkoutLike.objects.get_or_create(
            user=request.user,
            workout=workout
        )

        if not created:
            like.delete()
            return Response({'status': 'unliked'})

        serializer = self.get_serializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class WorkoutCommentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = WorkoutCommentSerializer

    def get_queryset(self):
        return WorkoutComment.objects.filter(
            workout_id=self.request.query_params.get('workout_id')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)