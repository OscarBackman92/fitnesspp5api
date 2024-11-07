from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import UserFollow, WorkoutLike, WorkoutComment
from .serializers import UserFollowSerializer, WorkoutLikeSerializer, WorkoutCommentSerializer
from workouts.models import Workout
from workouts.serializers import WorkoutSerializer
from api.permissions import IsOwnerOrReadOnly

class UserFollowViewSet(viewsets.ModelViewSet):
    serializer_class = UserFollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = UserFollow.objects.select_related('follower', 'following')
        
        filter_type = self.request.query_params.get('type', None)
        if filter_type == 'followers':
            return queryset.filter(following=self.request.user)
        elif filter_type == 'following':
            return queryset.filter(follower=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    @action(detail=False, methods=['POST'])
    def toggle_follow(self, request):
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                return Response(
                    {'error': 'user_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_to_follow = get_object_or_404(User, id=user_id)
            
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

            return Response(
                UserFollowSerializer(follow, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def followers_count(self, request):
        count = UserFollow.objects.filter(following=request.user).count()
        return Response({'followers_count': count})

    @action(detail=False, methods=['GET'])
    def following_count(self, request):
        count = UserFollow.objects.filter(follower=request.user).count()
        return Response({'following_count': count})

    @action(detail=False, methods=['GET'])
    def get_feed(self, request):
        """Get a feed of workouts from followed users."""
        followed_users = UserFollow.objects.filter(follower=request.user).values_list('following', flat=True)
        workouts = Workout.objects.filter(user__in=followed_users).order_by('-date_logged')
        serializer = WorkoutSerializer(workouts, many=True)
        return Response(serializer.data)


class WorkoutLikeViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkoutLike.objects.select_related('user', 'workout').filter(
            Q(user=self.request.user) | Q(workout__user=self.request.user)
        )

    def create(self, request, *args, **kwargs):
        try:
            workout_id = request.data.get('workout')
            if not workout_id:
                return Response(
                    {'error': 'workout_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            workout = get_object_or_404(Workout, id=workout_id)
            like, created = WorkoutLike.objects.get_or_create(
                user=request.user,
                workout=workout
            )

            if not created:
                like.delete()
                return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

            serializer = self.get_serializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['GET'])
    def likes_count(self, request, pk=None):
        workout = get_object_or_404(Workout, id=pk)
        count = WorkoutLike.objects.filter(workout=workout).count()
        return Response({'likes_count': count})


class WorkoutCommentViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        workout_id = self.request.query_params.get('workout_id')
        queryset = WorkoutComment.objects.select_related('user', 'workout').order_by('-created_at')
        
        if workout_id:
            queryset = queryset.filter(workout_id=workout_id)
        return queryset

    def perform_create(self, serializer):
        try:
            workout_id = self.request.data.get('workout')
            if not workout_id:
                raise ValidationError('workout_id is required')

            workout = get_object_or_404(Workout, id=workout_id)
            serializer.save(user=self.request.user, workout=workout)
        except Exception as e:
            raise ValidationError(str(e))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'Not authorized to delete this comment'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def comments_count(self, request):
        workout_id = request.query_params.get('workout_id')
        if not workout_id:
            return Response({'error': 'workout_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        count = WorkoutComment.objects.filter(workout_id=workout_id).count()
        return Response({'comments_count': count})
