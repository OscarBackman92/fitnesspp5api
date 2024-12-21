from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import WorkoutPost, Like, Comment
from .serializers import WorkoutPostSerializer, CommentSerializer
from workouts.models import Workout
import logging

logger = logging.getLogger(__name__)


class WorkoutPostViewSet(viewsets.ModelViewSet):
    """ViewSet for managing workout posts and their interactions."""
    serializer_class = WorkoutPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return optimized queryset for workout posts."""
        return WorkoutPost.objects.select_related(
            'user',
            'workout'
        ).prefetch_related(
            'likes',
            'comments',
            'comments__user'
        ).order_by('-created_at')

    @transaction.atomic
    def create(self, request):
        """Create a new workout post."""
        workout_id = request.data.get('workout_id')
        if not workout_id:
            return Response(
                {'error': 'workout_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            workout = get_object_or_404(Workout, id=workout_id)
            if workout.owner != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )

            post = WorkoutPost.objects.create(
                user=request.user,
                workout=workout
            )
            serializer = self.get_serializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating workout post: {str(e)}")
            return Response(
                {'error': 'Failed to create post'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        """Toggle like status on a workout post."""
        try:
            post = self.get_object()
            like, created = Like.objects.get_or_create(
                user=request.user,
                post=post
            )

            if not created:
                like.delete()
                return Response({'status': 'unliked'})

            return Response({'status': 'liked'})

        except Exception as e:
            logger.error(f"Error processing like: {str(e)}")
            return Response(
                {'error': 'Failed to process like'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['GET', 'POST'])
    def comments(self, request, pk=None):
        """Get or create comments on a workout post."""
        post = self.get_object()

        if request.method == 'GET':
            comments = post.comments.select_related('user')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        try:
            with transaction.atomic():
                serializer = CommentSerializer(
                    data={'content': request.data.get('content')})
                if serializer.is_valid():
                    serializer.save(user=request.user, post=post)
                    return Response(
                        serializer.data, status=status.HTTP_201_CREATED)
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            return Response(
                {'error': 'Failed to create comment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing comments."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return comments belonging to the authenticated user."""
        return Comment.objects.select_related(
            'user',
            'post'
        ).filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new comment."""
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """Update a comment."""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete a comment."""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
