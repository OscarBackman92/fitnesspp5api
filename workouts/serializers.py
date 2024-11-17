from rest_framework import serializers
from .models import Workout, WorkoutLike, WorkoutComment
from django.utils import timezone

class WorkoutSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    workout_type_display = serializers.CharField(
        source='get_workout_type_display', 
        read_only=True
    )
    likes_count = serializers.IntegerField(read_only=True, default=0)
    has_liked = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Workout
        fields = [
            'id', 
            'username', 
            'title',
            'workout_type', 
            'workout_type_display',
            'date_logged', 
            'duration', 
            'intensity', 
            'notes',
            'created_at', 
            'updated_at',
            'likes_count',
            'has_liked',
            'comments_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return WorkoutLike.objects.filter(
                workout=obj, 
                user=request.user
            ).exists()
        return False

    def validate_title(self, value):
        """Validate workout title."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

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
        
        # Set default title if not provided
        if 'title' not in data or not data['title']:
            workout_type = data.get('workout_type', '').title()
            data['title'] = f"{workout_type} Workout"
            
        return data

class WorkoutLikeSerializer(serializers.ModelSerializer):
<<<<<<< HEAD
    username = serializers.ReadOnlyField(source='user.username')
    workout_title = serializers.ReadOnlyField(source='workout.title')

    class Meta:
        model = WorkoutLike
        fields = ['id', 'workout', 'user', 'created_at', 'username', 'workout_title']
=======
    class Meta:
        model = WorkoutLike
        fields = ['id', 'workout', 'user', 'created_at']
>>>>>>> 49de782 (feat: Add title field and optimize workout models)
        read_only_fields = ['id', 'user', 'created_at']

class WorkoutCommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
<<<<<<< HEAD

    class Meta:
        model = WorkoutComment
        fields = ['id', 'workout', 'user', 'username', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
=======
    
    class Meta:
        model = WorkoutComment
        fields = ['id', 'workout', 'user', 'username', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
>>>>>>> 49de782 (feat: Add title field and optimize workout models)
