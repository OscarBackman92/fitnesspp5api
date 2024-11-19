from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import WorkoutPost, Like, Comment
from .serializers import WorkoutPostSerializer, CommentSerializer
from workouts.models import Workout


class WorkoutPostViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return the WorkoutPosts with related 'user' and 'workout'."""
        return WorkoutPost.objects.select_related(
            'user',
            'workout'
        ).prefetch_related(
            'likes',
            'comments'
        ).order_by('-created_at')

    def create(self, request):
        workout_id = request.data.get('workout_id')
        if not workout_id:
            return Response(
                {'error': 'workout_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        workout = get_object_or_404(Workout, id=workout_id)

        if workout.user != request.user:
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

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            like.delete()
            return Response({'status': 'unliked'})

        return Response({'status': 'liked'})

    @action(detail=True, methods=['GET', 'POST'])
    def comments(self, request, pk=None):
        post = self.get_object()

        if request.method == 'GET':
            comments = post.comments.select_related('user')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return comments belonging to the authenticated user."""
        return Comment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically assign the authenticated user to the comment."""
        serializer.save(user=self.request.user)
