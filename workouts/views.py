from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .models import Workout
from .serializers import WorkoutSerializer
from api.permissions import IsOwnerOrReadOnly
from django.db.models.functions import TruncDate

from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class WorkoutViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing workouts."""
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return objects for the current authenticated user or filtered by user_id."""
        user_id = self.request.query_params.get('user_id')
        queryset = Workout.objects.all()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=self.request.user)
            
        return queryset.order_by('-date_logged')

    def perform_create(self, serializer):
        """Save the workout with the current user."""
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Custom delete to handle errors gracefully."""
        try:
            workout = self.get_object()
            workout.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting workout: {str(e)}")
            return Response(
                {'error': 'Failed to delete workout'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """Get workout statistics."""
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        try:
            week_start = today - timedelta(days=today.weekday())
            workouts_this_week = queryset.filter(
                date_logged__gte=week_start,
                date_logged__lte=today
            ).count()
            
            # Optimize the `workouts_by_date` query to avoid repeating the same query
            workouts_by_date = queryset.annotate(
                workout_date=TruncDate('date_logged')
            ).values('workout_date').distinct().order_by('-workout_date')

            current_streak = 0
            check_date = today

            # Avoid calling filter twice
            if workouts_by_date:
                if not any(workout['workout_date'] == today for workout in workouts_by_date):
                    check_date = today - timedelta(days=1)

                while any(workout['workout_date'] == check_date for workout in workouts_by_date):
                    current_streak += 1
                    check_date = check_date - timedelta(days=1)

            workout_types = (
                queryset.values('workout_type')
                .annotate(
                    count=Count('id'),
                    total_duration=Sum('duration'),
                    avg_duration=Avg('duration')
                )
                .order_by('-count')
            )

            intensity_distribution = (
                queryset.values('intensity')
                .annotate(count=Count('id'))
                .order_by('intensity')
            )

            monthly_trends = (
                queryset.extra(select={'month': "DATE_TRUNC('month', date_logged)"}).values('month')
                .annotate(
                    workouts=Count('id'),
                    total_duration=Sum('duration')
                )
                .order_by('-month')[:12]
            )

            stats = {
                'total_workouts': queryset.count(),
                'workouts_this_week': workouts_this_week,
                'current_streak': current_streak,
                'total_duration': queryset.aggregate(Sum('duration'))['duration__sum'] or 0,
                'avg_duration': round(queryset.aggregate(Avg('duration'))['duration__avg'] or 0, 2),
                'workout_types': workout_types,
                'intensity_distribution': intensity_distribution,
                'monthly_trends': monthly_trends,
                'last_updated': timezone.now().isoformat()
            }

            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return Response(
                {'error': 'Failed to get statistics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        """Get workout summary with recent activity."""
        queryset = self.get_queryset()
        
        try:
            recent_workouts = queryset.order_by('-date_logged')[:5]
            
            summary = {
                'recent_workouts': WorkoutSerializer(recent_workouts, many=True).data,
                'total_workouts': queryset.count(),
                'total_duration': queryset.aggregate(Sum('duration'))['duration__sum'] or 0,
                'favorite_type': (
                    queryset.values('workout_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                    .first()
                ),
                'last_workout': WorkoutSerializer(
                    queryset.first()
                ).data if queryset.exists() else None
            }
            
            return Response(summary)
            
        except Exception as e:
            logger.error(f"Error getting workout summary: {str(e)}")
            return Response(
                {'error': 'Failed to get workout summary'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def types(self, request):
        """Get available workout types."""
        try:
            workout_types = [
                {'value': choice[0], 'label': choice[1]} 
                for choice in Workout.WORKOUT_TYPES
            ]
            return Response(workout_types)
        except Exception as e:
            logger.error(f"Error getting workout types: {str(e)}")
            return Response(
                {'error': 'Failed to get workout types'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
