from rest_framework import serializers
from .models import Workout, WorkoutLike, WorkoutComment
from django.utils import timezone
from rest_framework import serializers
from .models import Workout

class WorkoutSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    workout_type_display = serializers.CharField(
        source='get_workout_type_display', 
        read_only=True
    )

    class Meta:
        model = Workout
        fields = [
            'id', 'username', 'workout_type', 'workout_type_display',
            'date_logged', 'duration', 'intensity', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_duration(self, value):
        """Validate that duration is positive and within bounds."""
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0")
        if value > 1440:  # 24 hours in minutes
            raise serializers.ValidationError("Duration cannot exceed 24 hours")
        return value

    def validate(self, data):
        """Additional validation if needed."""
        if data.get('date_logged') and data['date_logged'] > timezone.now().date():
            raise serializers.ValidationError(
                {"date_logged": "Cannot log workouts in the future"}
            )
        return data