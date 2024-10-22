from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.contrib.auth.models import User
from .models import UserFollow, WorkoutLike, WorkoutComment
from .serializers import (UserFollowSerializer, WorkoutLikeSerializer, WorkoutCommentSerializer)
from workouts.models import Workout
from workouts.serializers import WorkoutSerializer

class SocialFeedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserFollowViewSet(viewsets.ModelViewSet):
    serializer_class = UserFollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SocialFeedPagination

    def get_queryset(self):
        return UserFollow.objects.filter(follower=self.request.user)

    @action(detail=False, methods=['post'])
    def follow(self, request):
        user_to_follow_id = request.data.get('user_id')
        if user_to_follow_id == request.user.id:
            return Response(
                {'error': 'Cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            follow, created = UserFollow.objects.get_or_create(
                follower=request.user,
                following_id=user_to_follow_id
            )
            return Response(
                UserFollowSerializer(follow).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def unfollow(self, request):
        user_to_unfollow_id = request.data.get('user_id')
        follow = get_object_or_404(
            UserFollow,
            follower=request.user,
            following_id=user_to_unfollow_id
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class WorkoutLikeViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutLikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkoutLike.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        workout_id = request.data.get('workout')
        workout = get_object_or_404(Workout, id=workout_id)
        
        like, created = WorkoutLike.objects.get_or_create(
            user=request.user,
            workout=workout
        )
        
        serializer = self.get_serializer(like)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

class WorkoutCommentViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkoutComment.objects.filter(workout__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SocialFeedView(generics.ListAPIView):
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SocialFeedPagination

    def get_queryset(self):
        following_users = UserFollow.objects.filter(
            follower=self.request.user
        ).values_list('following', flat=True)
        
        return Workout.objects.filter(
            user__in=following_users
        ).select_related('user').prefetch_related(
            'likes',
            'comments'
        ).order_by('-created_at')