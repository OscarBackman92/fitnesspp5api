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
        """Return objects for the current authenticated user only."""
        return Workout.objects.filter(user=self.request.user).order_by('-date_logged')

    def perform_create(self, serializer):
        """Save the workout with the current user."""
        serializer.save(user=self.request.user) 

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
            workouts_by_date = queryset.annotate(
                workout_date=TruncDate('date_logged')
            ).values('workout_date').distinct().order_by('-workout_date')

            current_streak = 0
            check_date = today

            if not workouts_by_date.filter(workout_date=today).exists():
                check_date = today - timedelta(days=1)

            while workouts_by_date.filter(workout_date=check_date).exists():
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
                queryset.extra(select={'month': "DATE_TRUNC('month', date_logged)"})
                .values('month')
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