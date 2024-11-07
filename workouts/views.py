# views.py

import logging
from django.db.models import Sum, Avg, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Workout
from .serializers import WorkoutSerializer
from api.permissions import IsOwnerOrReadOnly
from datetime import timedelta

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
    ordering_fields = ['date_logged', 'duration', 'calories']
    ordering = ['-date_logged']  # Default ordering

    def get_queryset(self):
        """
        Get base queryset filtered by user and optionally by date range.
        Allows filtering by start_date and end_date query parameters.
        """
        queryset = Workout.objects.filter(user=self.request.user)
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        try:
            if start_date:
                queryset = queryset.filter(date_logged__gte=start_date)
            if end_date:
                queryset = queryset.filter(date_logged__lte=end_date)
        except ValueError as e:
            logger.warning(f"Invalid date format in query parameters: {str(e)}")

        return queryset.select_related('user')

    def perform_create(self, serializer):
        """Create a new workout instance"""
        try:
            workout = serializer.save(user=self.request.user)
            logger.info(f"Workout created successfully for user {self.request.user.id}")
            return workout
        except Exception as e:
            logger.error(f"Error creating workout for user {self.request.user.id}: {str(e)}")
            raise

    def perform_update(self, serializer):
        """Update a workout instance"""
        try:
            workout = serializer.save()
            logger.info(f"Workout {workout.id} updated successfully")
            return workout
        except Exception as e:
            logger.error(f"Error updating workout {serializer.instance.id}: {str(e)}")
            raise

    def perform_destroy(self, instance):
        """Delete a workout instance"""
        try:
            workout_id = instance.id
            instance.delete()
            logger.info(f"Workout {workout_id} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting workout {instance.id}: {str(e)}")
            raise

    def update(self, request, *args, **kwargs):
        """Handle workout updates with validation"""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=kwargs.get('partial', False)
        )
        
        if serializer.is_valid():
            try:
                self.perform_update(serializer)
                logger.info(f"Workout updated successfully for user {request.user.id}")
                return Response(serializer.data)
            except Exception as e:
                logger.error(f"Error during workout update: {str(e)}")
                return Response({
                    'status': 'Error',
                    'message': 'An error occurred while updating the workout.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.error(f"Validation error for user {request.user.id}: {serializer.errors}")
        return Response({
            'status': 'Bad request',
            'message': 'Workout could not be updated with received data.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Generate a summary of user's workout statistics.
        Includes total workouts, durations, calories, and trends.
        """
        try:
            user_workouts = self.get_queryset()
            today = timezone.now().date()
            last_week = today - timezone.timedelta(days=7)
            last_month = today - timezone.timedelta(days=30)
            
            # Calculate basic statistics
            total_workouts = user_workouts.count()
            stats = user_workouts.aggregate(
                total_duration=Sum('duration'),
                total_calories=Sum('calories'),
                avg_duration=Avg('duration')
            )

            # Get most frequent workout type
            most_frequent = (
                user_workouts
                .values('workout_type')
                .annotate(count=Count('id'))
                .order_by('-count')
                .first()
            )

            return Response({
                'total_workouts': total_workouts,
                'total_duration': stats['total_duration'] or 0,
                'total_calories': stats['total_calories'] or 0,
                'avg_duration': round(stats['avg_duration'] or 0, 2),
                'most_frequent_workout': most_frequent['workout_type'] if most_frequent else None,
                'recent_workouts': WorkoutSerializer(
                    user_workouts.order_by('-date_logged')[:5], 
                    many=True
                ).data,
                'workouts_this_week': user_workouts.filter(
                    date_logged__gte=last_week
                ).count(),
                'workouts_this_month': user_workouts.filter(
                    date_logged__gte=last_month
                ).count()
            })
        except Exception as e:
            logger.error(f"Error generating workout summary for user {request.user.id}: {str(e)}")
            return Response({
                'status': 'Error',
                'message': 'An error occurred while generating the workout summary.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Provide detailed workout statistics including trends and patterns.
        """
        try:
            queryset = self.get_queryset()
            
            return Response({
                'workout_types': self._get_workout_type_distribution(queryset),
                'monthly_trends': self._get_monthly_trends(queryset),
                'intensity_distribution': self._get_intensity_distribution(queryset),
                'streaks': self._calculate_streaks(queryset),
            })
        except Exception as e:
            logger.error(f"Error generating statistics for user {request.user.id}: {str(e)}")
            return Response({
                'status': 'Error',
                'message': 'An error occurred while generating statistics.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_workout_type_distribution(self, queryset):
        """Calculate distribution of workout types"""
        return (
            queryset
            .values('workout_type')
            .annotate(
                count=Count('id'),
                total_duration=Sum('duration'),
                total_calories=Sum('calories'),
                avg_duration=Avg('duration')
            )
            .order_by('-count')
        )

    def _get_monthly_trends(self, queryset):
        """Calculate monthly workout trends"""
        return (
            queryset
            .annotate(month=TruncMonth('date_logged'))
            .values('month')
            .annotate(
                workout_count=Count('id'),
                total_duration=Sum('duration'),
                total_calories=Sum('calories'),
                avg_duration=Avg('duration')
            )
            .order_by('month')
        )

    def _get_intensity_distribution(self, queryset):
        """Calculate distribution of workout intensities"""
        return (
            queryset
            .values('intensity')
            .annotate(
                count=Count('id'),
                avg_duration=Avg('duration'),
                avg_calories=Avg('calories'),
                total_duration=Sum('duration'),
                total_calories=Sum('calories')
            )
            .order_by('intensity')
        )

    def _calculate_streaks(self, queryset):
        """Calculate workout streaks"""
        today = timezone.now().date()
        
        # Get all workout dates ordered
        dates = list(
            queryset
            .filter(date_logged__lte=today)
            .values_list('date_logged', flat=True)
            .order_by('date_logged')
            .distinct()
        )

        if not dates:
            return {'current_streak': 0, 'longest_streak': 0}

        # Calculate streaks
        current_streak = 1
        longest_streak = 1
        current_count = 1

        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_count += 1
                longest_streak = max(longest_streak, current_count)
            else:
                current_count = 1

        # Check if current streak is active
        if (today - dates[-1]).days <= 1:
            current_streak = current_count
        else:
            current_streak = 0

        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'last_workout': dates[-1].isoformat() if dates else None,
            'first_workout': dates[0].isoformat() if dates else None,
            'total_active_days': len(dates)
        }