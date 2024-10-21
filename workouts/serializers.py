from rest_framework import serializers
from .models import Workout

class WorkoutSerializer(serializers.ModelSerializer):
    workout_type_display = serializers.CharField(source='get_workout_type_display', read_only=True)
    duration_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = Workout
        fields = ['id', 'user', 'workout_type', 'workout_type_display', 'date_logged', 
                  'duration', 'duration_hours', 'calories', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)