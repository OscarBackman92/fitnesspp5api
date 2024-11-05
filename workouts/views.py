import logging
from django.db.models import Sum, Avg
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Workout
from .serializers import WorkoutSerializer
from api.permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)

class WorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['workout_type', 'date_logged']
    search_fields = ['workout_type', 'notes']
    ordering_fields = ['date_logged', 'duration', 'calories']

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        
        if serializer.is_valid():
            self.perform_update(serializer)
            logger.info(f"Workout updated successfully for user {request.user.id}")
            return Response(serializer.data)
        
        logger.error(f"Validation error for user {request.user.id}: {serializer.errors}")
        return Response({
            'status': 'Bad request',
            'message': 'Workout could not be updated with received data.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        try:
            user_workouts = self.get_queryset()
            today = timezone.now().date()
            last_week, last_month = self._get_date_ranges(today)
            
            summary_data = self._calculate_summary(user_workouts, last_week, last_month)
            return Response(summary_data)
        except Exception as e:
            logger.error(f"Error generating workout summary for user {request.user.id}: {str(e)}")
            return Response({
                'status': 'Error',
                'message': 'An error occurred while generating the workout summary.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_date_ranges(self, today):
        """Return the date ranges for the last week and last month."""
        last_week = today - timezone.timedelta(days=7)
        last_month = today - timezone.timedelta(days=30)
        return last_week, last_month

    def _calculate_summary(self, user_workouts, last_week, last_month):
        """Calculate summary statistics for workouts."""
        total_workouts = user_workouts.count()
        total_duration = user_workouts.aggregate(Sum('duration'))['duration__sum'] or 0
        total_calories = user_workouts.aggregate(Sum('calories'))['calories__sum'] or 0
        avg_duration = user_workouts.aggregate(Avg('duration'))['duration__avg'] or 0

        recent_workouts = user_workouts.order_by('-date_logged')[:5]
        workouts_this_week = user_workouts.filter(date_logged__gte=last_week).count()
        workouts_this_month = user_workouts.filter(date_logged__gte=last_month).count()

        return {
            'total_workouts': total_workouts,
            'total_duration': total_duration,
            'total_calories': total_calories,
            'avg_duration': avg_duration,
            'recent_workouts': WorkoutSerializer(recent_workouts, many=True).data,
            'workouts_this_week': workouts_this_week,
            'workouts_this_month': workouts_this_month
        }
