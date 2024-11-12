from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import UserFollow, WorkoutLike, WorkoutComment, WorkoutPost
from workouts.models import Workout
from .serializers import (
    UserFollowSerializer,
    WorkoutLikeSerializer,
    WorkoutCommentSerializer,
    WorkoutPostSerializer,
    FeedSerializer
)
from api.permissions import IsOwnerOrReadOnly
class SocialFeedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FeedSerializer
    filterset_fields = ['user']
    search_fields = ['caption', 'workout__notes']
    ordering_fields = ['shared_at', 'likes_count', 'comments_count']

    def get_queryset(self):
        following = UserFollow.objects.filter(
            follower=self.request.user
        ).values_list('following', flat=True)
        
        return WorkoutPost.objects.filter(
            Q(user__in=list(following)) | Q(user=self.request.user)
        ).annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).order_by('-shared_at')

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """Get social stats for a user"""
        user_id = request.query_params.get('user_id', request.user.id)
        target_user = get_object_or_404(User, id=user_id)

        # Base counts
        followers_count = UserFollow.objects.filter(following=target_user).count()
        following_count = UserFollow.objects.filter(follower=target_user).count()
        posts_count = WorkoutPost.objects.filter(user=target_user).count()

        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_posts = WorkoutPost.objects.filter(
            user=target_user,
            shared_at__gte=thirty_days_ago
        )
        recent_posts_count = recent_posts.count()

        # Engagement metrics
        recent_likes = WorkoutLike.objects.filter(
            workout_post__user=target_user,
            created_at__gte=thirty_days_ago
        ).count()
        
        recent_comments = WorkoutComment.objects.filter(
            workout_post__user=target_user,
            created_at__gte=thirty_days_ago
        ).count()

        # Calculate engagement rate
        engagement_rate = 0
        if recent_posts_count > 0:
            engagement_rate = round(
                ((recent_likes + recent_comments) / recent_posts_count) * 100,
                2
            )

        # Top posts
        top_posts = recent_posts.annotate(
            engagement=Count('likes') + Count('comments')
        ).order_by('-engagement')[:3]

        return Response({
            'user_id': target_user.id,
            'username': target_user.username,
            'followers_count': followers_count,
            'following_count': following_count,
            'posts_count': posts_count,
            'recent_activity': {
                'posts_count': recent_posts_count,
                'likes_received': recent_likes,
                'comments_received': recent_comments,
                'engagement_rate': engagement_rate
            },
            'top_posts': WorkoutPostSerializer(top_posts, many=True).data,
            'is_following': UserFollow.objects.filter(
                follower=request.user,
                following=target_user
            ).exists() if request.user != target_user else None
        })

    @action(detail=False, methods=['GET'])
    def feed(self, request):
        """Get paginated social feed"""
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        start = (page - 1) * limit
        end = start + limit

        queryset = self.get_queryset()[start:end]
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'results': serializer.data,
            'next': page + 1 if end < self.get_queryset().count() else None,
            'count': self.get_queryset().count()
        })

    @action(detail=False, methods=['POST'])
    def share_workout(self, request):
        """Share a workout to the social feed"""
        workout_id = request.data.get('workout_id')
        caption = request.data.get('caption', '')
        
        workout = get_object_or_404(Workout, id=workout_id)
        
        # Check if workout is already shared
        if WorkoutPost.objects.filter(workout=workout, user=request.user).exists():
            return Response(
                {'error': 'Workout already shared'},
                status=status.HTTP_400_BAD_REQUEST
            )

        post = WorkoutPost.objects.create(
            workout=workout,
            user=request.user,
            caption=caption
        )

        serializer = WorkoutPostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserFollowViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserFollowSerializer
    
    def get_queryset(self):
        return UserFollow.objects.filter(
            Q(follower=self.request.user) | Q(following=self.request.user)
        )

    @action(detail=False, methods=['POST'])
    def toggle_follow(self, request):
        """Toggle following status for a user"""
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

    @action(detail=False, methods=['GET'])
    def followers(self, request):
        """Get list of followers"""
        user_id = request.query_params.get('user_id', request.user.id)
        followers = UserFollow.objects.filter(following_id=user_id)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def following(self, request):
        """Get list of users being followed"""
        user_id = request.query_params.get('user_id', request.user.id)
        following = UserFollow.objects.filter(follower_id=user_id)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)

class WorkoutLikeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = WorkoutLikeSerializer
    queryset = WorkoutLike.objects.all()

    @action(detail=False, methods=['POST'])
    def toggle(self, request):
        """Toggle like status for a workout"""
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

    def get_queryset(self):
        return WorkoutLike.objects.filter(user=self.request.user)

class WorkoutCommentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = WorkoutCommentSerializer
    queryset = WorkoutComment.objects.all()

    def get_queryset(self):
        return WorkoutComment.objects.filter(
            workout_post_id=self.request.query_params.get('post_id')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)