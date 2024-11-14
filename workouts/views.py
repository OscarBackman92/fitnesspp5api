from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .models import Workout
from .serializers import WorkoutSerializer
from api.permissions import IsOwnerOrReadOnly
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
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            logger.error(f"Error creating workout: {str(e)}")
            raise

    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """Get workout statistics."""
        queryset = self.get_queryset()
        
        try:
            stats = {
                'total_workouts': queryset.count(),
                'total_duration': queryset.aggregate(Sum('duration'))['duration__sum'] or 0,
                'avg_duration': round(queryset.aggregate(Avg('duration'))['duration__avg'] or 0, 2),
                'workout_types': queryset.values('workout_type').annotate(
                    count=Count('id'),
                    total_duration=Sum('duration'),
                    avg_duration=Avg('duration')
                ),
                'intensity_distribution': queryset.values('intensity').annotate(count=Count('id')),
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
        """Get a summary of workout data."""
        queryset = self.get_queryset()
        total_workouts = queryset.count()
        stats = queryset.aggregate(
            total_duration=Sum('duration'),
            avg_duration=Avg('duration')
        )
        
        return Response({
            'total_workouts': total_workouts,
            'total_duration': stats['total_duration'] or 0,
            'avg_duration': round(stats['avg_duration'] or 0, 2),
            'recent_workouts': WorkoutSerializer(
                queryset.order_by('-date_logged')[:5],
                many=True
            ).data
        })

def _calculate_streaks(self, queryset):
    """Calculate workout streaks with proper handling of current day."""
    from datetime import datetime, timedelta
    
    dates = list(
        queryset.order_by('date_logged')
        .values_list('date_logged', flat=True)
        .distinct()
    )
    
    if not dates:
        return {
            'current_streak': 0,
            'longest_streak': 0,
            'total_active_days': 0
        }

    workout_dates = set(date.isoformat() for date in dates)
    
    today = timezone.now().date()
    current_streak = 0
    check_date = today
    
    while check_date.isoformat() in workout_dates or (
        check_date == today and
        (check_date - timedelta(days=1)).isoformat() in workout_dates
    ):
        if check_date.isoformat() in workout_dates:
            current_streak += 1
        check_date = check_date - timedelta(days=1)

    longest_streak = 0
    current_count = 0
    dates_sorted = sorted(dates)
    
    for i in range(len(dates_sorted)):
        if i == 0 or (dates_sorted[i] - dates_sorted[i-1]).days == 1:
            current_count += 1
        else:
            longest_streak = max(longest_streak, current_count)
            current_count = 1
    
    longest_streak = max(longest_streak, current_count)

    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'first_workout': dates_sorted[0].isoformat(),
        'last_workout': dates_sorted[-1].isoformat(),
        'total_active_days': len(dates)
    }