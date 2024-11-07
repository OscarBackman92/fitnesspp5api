import logging
from dateutil.parser import parse, ParserError
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Workout
from .serializers import WorkoutSerializer
from api.permissions import IsOwnerOrReadOnly
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class WorkoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing workout operations.
    Provides CRUD operations and additional functionality for workout data.
    """
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['workout_type', 'date_logged', 'intensity']
    search_fields = ['workout_type', 'notes']
    ordering_fields = ['date_logged', 'duration']
    ordering = ['-date_logged']  # Default ordering

    def get_queryset(self):
        """Get base queryset filtered by user and optionally by date range."""
        queryset = Workout.objects.filter(user=self.request.user)

        # Date filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            try:
                parsed_start_date = parse(start_date)
                queryset = queryset.filter(date_logged__gte=parsed_start_date)
            except (ValueError, ParserError):
                logger.warning(f"Invalid start_date format: {start_date}")
                raise ValidationError("Invalid start_date format. It must be in YYYY-MM-DD format.")

        if end_date:
            try:
                parsed_end_date = parse(end_date)
                queryset = queryset.filter(date_logged__lte=parsed_end_date)
            except (ValueError, ParserError):
                logger.warning(f"Invalid end_date format: {end_date}")
                raise ValidationError("Invalid end_date format. It must be in YYYY-MM-DD format.")

        return queryset.select_related('user')

    def perform_create(self, serializer):
        """Create a new workout instance and log the action."""
        workout = serializer.save(user=self.request.user)
        logger.info(f"Workout created successfully for user {self.request.user.id}: {workout}")

    def perform_update(self, serializer):
        """Update a workout instance and log the action."""
        workout = serializer.save()
        logger.info(f"Workout updated successfully: {workout}")

    def perform_destroy(self, instance):
        """Delete a workout instance and log the action."""
        workout_id = instance.id
        instance.delete()
        logger.info(f"Workout deleted successfully: {workout_id}")

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Generate a summary of user's workout statistics."""
        user_workouts = self.get_queryset()
        total_workouts = user_workouts.count()
        stats = user_workouts.aggregate(
            total_duration=Sum('duration') or 0,
            avg_duration=Avg('duration') or 0
        )

        # Handle None values for avg_duration
        avg_duration = stats['avg_duration']
        if avg_duration is None:
            avg_duration = 0  # Set to 0 or another default value if there are no workouts

        return Response({
            'total_workouts': total_workouts,
            'total_duration': stats['total_duration'],
            'avg_duration': round(avg_duration, 2),
            'recent_workouts': WorkoutSerializer(user_workouts.order_by('-date_logged')[:5], many=True).data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Provide detailed workout statistics including trends and patterns."""
        queryset = self.get_queryset()

        return Response({
            'workout_types': self._get_workout_type_distribution(queryset),
            'monthly_trends': self._get_monthly_trends(queryset),
            'intensity_distribution': self._get_intensity_distribution(queryset),
            'streaks': self._calculate_streaks(queryset),
        })

    def _get_workout_type_distribution(self, queryset):
        """Calculate distribution of workout types."""
        return (
            queryset
            .values('workout_type')
            .annotate(
                count=Count('id'),
                total_duration=Sum('duration'),
                avg_duration=Avg('duration')
            )
            .order_by('-count')
        )

    def _get_monthly_trends(self, queryset):
        """Calculate monthly workout trends."""
        return (
            queryset
            .annotate(month=TruncMonth('date_logged'))
            .values('month')
            .annotate(
                workout_count=Count('id'),
                total_duration=Sum('duration'),
                avg_duration=Avg('duration')
            )
            .order_by('month')
        )

    def _get_intensity_distribution(self, queryset):
        """Calculate distribution of workout intensities."""
        return (
            queryset
            .values('intensity')
            .annotate(
                count=Count('id'),
                avg_duration=Avg('duration'),
                total_duration=Sum('duration')
            )
            .order_by('intensity')
        )

    def _calculate_streaks(self, queryset):
        """Calculate workout streaks."""
        today = timezone.now().date()
        dates = list(
            queryset
            .filter(date_logged__lte=today)
            .values_list('date_logged', flat=True)
            .order_by('date_logged')
            .distinct()
        )

        if not dates:
            return {'current_streak': 0, 'longest_streak': 0}

        current_streak = 0
        longest_streak = 0
        current_count = 0

        for i in range(len(dates) - 1):
            if (dates[i + 1] - dates[i]).days == 1:
                current_count += 1
            else:
                longest_streak = max(longest_streak, current_count)
                current_count = 0

        current_streak = current_count + 1 if (today - dates[-1]).days <= 1 else 0
        longest_streak = max(longest_streak, current_count)

        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'last_workout': dates[-1].isoformat() if dates else None,
            'first_workout': dates[0].isoformat() if dates else None,
            'total_active_days': len(dates)
        }
