# workouts/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .models import Workout
from .serializers import WorkoutSerializer
from api.permissions import IsOwnerOrReadOnly
import logging
from dateutil.parser import parse, ParserError

logger = logging.getLogger(__name__)

class WorkoutViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing workouts."""
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Workout.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['workout_type', 'date_logged', 'intensity']

    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Save the workout with the current user."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """Get statistics about workouts."""
        queryset = self.get_queryset()
        stats = {
            'workout_types': queryset.values('workout_type').annotate(
                count=Count('id'),
                total_duration=Sum('duration'),
                avg_duration=Avg('duration')
            ),
            'monthly_trends': queryset.annotate(
                month=TruncMonth('date_logged')
            ).values('month').annotate(
                count=Count('id'),
                total_duration=Sum('duration'),
                avg_duration=Avg('duration')
            ).order_by('month'),
            'intensity_distribution': queryset.values('intensity').annotate(
                count=Count('id'),
                total_duration=Sum('duration')
            ),
            'streaks': self._calculate_streaks(queryset)
        }
        return Response(stats)

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
        """Calculate workout streaks."""
        dates = list(
            queryset.order_by('date_logged')
            .values_list('date_logged', flat=True)
            .distinct()
        )
        
        if not dates:
            return {'current_streak': 0, 'longest_streak': 0}

        current_streak = 1
        longest_streak = 1
        current_count = 1

        for i in range(len(dates) - 1):
            if (dates[i + 1] - dates[i]).days == 1:
                current_count += 1
                current_streak = max(current_streak, current_count)
            else:
                longest_streak = max(longest_streak, current_count)
                current_count = 1

        longest_streak = max(longest_streak, current_count)

        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'first_workout': dates[0].isoformat(),
            'last_workout': dates[-1].isoformat(),
            'total_active_days': len(dates)
        }