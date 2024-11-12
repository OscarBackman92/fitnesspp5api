from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import UserFollow, WorkoutLike, WorkoutComment
from .serializers import (
    UserFollowSerializer, 
    WorkoutLikeSerializer, 
    WorkoutCommentSerializer,
    FeedSerializer
)
from workouts.models import Workout

class SocialFeedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FeedSerializer

    def get_queryset(self):
        # Get users that the current user follows
        following = UserFollow.objects.filter(
            follower=self.request.user
        ).values_list('following', flat=True)

        # Get workouts from followed users and the current user
        return Workout.objects.filter(
            user__in=list(following) + [self.request.user.id]
        ).order_by('-created_at')

    @action(detail=False, methods=['GET'])
    def feed(self, request):
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        start = (page - 1) * limit
        end = start + limit

        queryset = self.get_queryset()[start:end]
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'results': serializer.data,
            'next': page + 1 if end < self.get_queryset().count() else None,
            'count': self.get_queryset().count()
        })

class UserFollowViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserFollowSerializer

    def get_queryset(self):
        return UserFollow.objects.filter(follower=self.request.user)

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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkoutLikeSerializer

    def get_queryset(self):
        return WorkoutLike.objects.filter(user=self.request.user)

    @action(detail=False, methods=['POST'])
    def toggle(self, request):
        workout = get_object_or_404(Workout, id=request.data.get('workout_id'))
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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkoutCommentSerializer

    def get_queryset(self):
        workout_id = self.request.query_params.get('workout_id')
        queryset = WorkoutComment.objects.all()
        if workout_id:
            queryset = queryset.filter(workout_id=workout_id)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)