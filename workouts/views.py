from django.db.models import Count
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsOwnerOrReadOnly
from .models import Workout, WorkoutComment
from .serializers import WorkoutSerializer, WorkoutCommentSerializer, WorkoutCommentDetailSerializer

class WorkoutList(generics.ListCreateAPIView):
    """
    List workouts or create a workout if logged in.
    The perform_create method associates the workout with the logged in user.
    """
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Workout.objects.annotate(
        likes_count=Count('workoutlike', distinct=True),
        comments_count=Count('workoutcomment', distinct=True)
    ).order_by('-created_at')
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        'owner__profile',
        'owner__followed__owner__profile',
        'workoutlike__owner__profile',
    ]
    search_fields = [
        'owner__username',
        'title',
        'workout_type',
    ]
    ordering_fields = [
        'likes_count',
        'comments_count',
        'workoutlike__created_at',
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class WorkoutDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve a workout and edit or delete it if you own it.
    """
    serializer_class = WorkoutSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Workout.objects.annotate(
        likes_count=Count('workoutlike', distinct=True),
        comments_count=Count('workoutcomment', distinct=True)
    ).order_by('-created_at')

class WorkoutCommentList(generics.ListCreateAPIView):
    """
    List comments or create a comment if logged in.
    """
    serializer_class = WorkoutCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = WorkoutComment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['workout']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class WorkoutCommentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve a comment, or update or delete it by id if you own it.
    """
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = WorkoutCommentDetailSerializer
    queryset = WorkoutComment.objects.all()