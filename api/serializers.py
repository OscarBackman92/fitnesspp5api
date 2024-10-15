from rest_framework import serializers
from .models import UserProfile, Workout

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'weight', 'height', 'fitness_goals']

class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id', 'user', 'workout_type', 'duration', 'calories', 'date_logged']
