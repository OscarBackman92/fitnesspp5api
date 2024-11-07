from rest_framework import serializers
from .models import Workout

class WorkoutSerializer(serializers.ModelSerializer):
    workout_type_display = serializers.CharField(source='get_workout_type_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Workout
        fields = [
            'id', 'user', 'user_username', 'workout_type', 'workout_type_display',
            'date_logged', 'duration', 'calories', 'notes', 'created_at', 'updated_at',
            'intensity', 'likes_count', 'comments_count', 'is_liked'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

    def validate_duration(self, value):
        if value < 0:
            raise serializers.ValidationError("Duration cannot be negative.")
        return value

    def validate_calories(self, value):
        if value < 0:
            raise serializers.ValidationError("Calories cannot be negative.")
        return value