from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models import Workout
from .serializers import WorkoutSerializer
from config.permissions import IsOwnerOrReadOnly
import logging

logger = logging.getLogger(__name__)


class WorkoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing workouts.
    Supports CRUD operations and provides additional actions for
    statistics and summaries.
    """
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Return all workouts for detail views and restricted queryset for
        list views.
        """
        if self.action in ['list', 'create', 'statistics', 'summary']:
            return Workout.objects.filter(owner=self.request.user)
        return Workout.objects.all()

    def perform_create(self, serializer):
        """
        Save a new workout instance with the current user as the owner.
        """
        try:
            serializer.save(owner=self.request.user)
        except Exception as e:
            logger.error(
                f"Error creating workout by user {self.request.user}: {str(e)}"
            )
            raise

    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """
        Retrieve statistics about the user's workouts.
        Includes total workouts, duration, and aggregated workout data.
        """
        queryset = self.get_queryset()
        try:
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())

            stats = {
                'total_workouts': queryset.count(),
                'total_duration': queryset.aggregate(
                    Sum('duration')
                )['duration__sum'] or 0,
                'avg_duration': round(
                    queryset.aggregate(
                        Avg('duration'))['duration__avg'] or 0, 2
                ),
                'workouts_this_week': queryset.filter(
                    date_logged__gte=week_start
                ).count(),
                'workout_types': queryset.values('workout_type').annotate(
                    count=Count('id'),
                    total_duration=Sum('duration'),
                    avg_duration=Avg('duration')
                ),
                'intensity_distribution': queryset.values(
                    'intensity').annotate(
                    count=Count('id')
                ),
            }

            streak_data = self._calculate_streaks(queryset)
            stats.update(streak_data)

            return Response(stats, status=status.HTTP_200_OK)
        except ValueError as ve:
            logger.error(f"Value error during statistics calculation: {ve}")
            return Response(
                {'error': 'Invalid data for statistics'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Unexpected error during statistics calculation: {e}")
            return Response(
                {'error': 'Failed to get statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def summary(self, request):
        """
        Provide a summary of workout data for the authenticated user.
        Includes total workouts, average duration, and recent workouts.
        """
        queryset = self.get_queryset()
        try:
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
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting summary: {str(e)}")
            return Response(
                {'error': 'Failed to get summary'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _calculate_streaks(self, queryset):
        """
        Calculate workout streaks (current and longest).
        A streak is defined as consecutive days with logged workouts.

        Args:
            queryset: QuerySet of workouts to calculate streaks from

        Returns:
            dict: Contains current_streak, longest_streak, and other
            streak-related data.
        """
        dates = list(
            queryset.order_by('date_logged')
            .values_list('date_logged', flat=True)
            .distinct()
        )

        if not dates:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'first_workout': None,
                'last_workout': None,
                'total_active_days': 0
            }

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

        if (timezone.now().date() - dates[-1]).days > 1:
            current_streak = 0

        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'first_workout': dates[0].isoformat(),
            'last_workout': dates[-1].isoformat(),
            'total_active_days': len(dates)
        }
