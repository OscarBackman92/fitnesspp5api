from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, Workout

class UserProfileSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    bmi = serializers.FloatField(source='calculate_bmi', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'weight', 'height', 'fitness_goals', 'date_of_birth', 'age', 'bmi', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['profile'] = UserProfileSerializer(instance.userprofile).data
        return ret

class WorkoutSerializer(serializers.ModelSerializer):
    workout_type_display = serializers.CharField(source='get_workout_type_display', read_only=True)
    duration_hours = serializers.FloatField(source='get_duration_in_hours', read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Workout
        fields = ['id', 'user', 'workout_type', 'workout_type_display', 'date_logged', 'duration', 'duration_hours', 'calories', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)