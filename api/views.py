from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile
from .serializers import UserProfileSerializer
from workouts.models import Workout
from config.permissions import IsOwnerOrReadOnly
from rest_framework import permissions

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    @action(detail=True, methods=['GET'])
    def stats(self, request, pk=None):
        """Get user profile statistics."""
        try:
            profile = self.get_object()
            
            # Get the start of the current week
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())
            
            # Get user's workouts
            user_workouts = Workout.objects.filter(owner=profile.user)
            
            # Calculate weekly workouts
            weekly_workouts = user_workouts.filter(
                date_logged__gte=week_start
            ).count()

            # Calculate total workout time
            total_time = user_workouts.aggregate(
                total=Sum('duration')
            )['total'] or 0

            # Calculate streak
            streak = self.calculate_streak(user_workouts)

            stats = {
                'total_workouts': user_workouts.count(),
                'workouts_this_week': weekly_workouts,
                'total_workout_time': total_time,
                'current_streak': streak,
                # Additional stats
                'workouts_by_type': self.get_workouts_by_type(user_workouts),
                'followers_count': 0,  # Implement if you have followers
                'following_count': 0,  # Implement if you have following
            }

            return Response(stats)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def calculate_streak(self, workouts):
        """Calculate the current workout streak."""
        if not workouts.exists():
            return 0

        # Get dates of workouts in descending order
        workout_dates = workouts.order_by('-date_logged')\
            .values_list('date_logged', flat=True)
        
        current_streak = 1
        current_date = workout_dates[0]

        # Check consecutive days
        for date in workout_dates[1:]:
            if current_date - date == timedelta(days=1):
                current_streak += 1
                current_date = date
            else:
                break

        return current_streak

    def get_workouts_by_type(self, workouts):
        """Get workout count by type."""
        return workouts.values('workout_type')\
            .annotate(count=Count('id'))\
            .order_by('workout_type')