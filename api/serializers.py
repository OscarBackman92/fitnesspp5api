from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Goal
from django.db import IntegrityError
from cloudinary.utils import cloudinary_url
from django.utils import timezone

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    profile_image = serializers.SerializerMethodField()
    bmi = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    workouts_count = serializers.IntegerField(read_only=True)
    avg_workout_duration = serializers.FloatField(read_only=True)
    total_calories = serializers.IntegerField(read_only=True)
    goals = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'name', 'weight', 'height',
            'bmi', 'age', 'fitness_goals', 'profile_image',
            'date_of_birth', 'created_at', 'updated_at', 'gender',
            'is_owner', 'workouts_count', 'avg_workout_duration',
            'total_calories', 'goals'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_goals(self, obj):
        """Get user's goals with progress information"""
        return GoalSerializer(obj.user.goals.all(), many=True).data

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.user

    def get_profile_image(self, obj):
        if obj.profile_image:
            try:
                url, options = cloudinary_url(
                    str(obj.profile_image),
                    format='webp',
                    transformation=[
                        {'width': 200, 'height': 200, 'crop': 'fill', 'gravity': 'face'},
                        {'quality': 'auto:eco'},
                        {'fetch_format': 'auto'}
                    ]
                )
                return url
            except Exception as e:
                return None
        return None

    def get_bmi(self, obj):
        return obj.calculate_bmi()

    def get_age(self, obj):
        return obj.get_age()

    def validate_profile_image(self, value):
        if value:
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError(
                    'Image size cannot exceed 2MB'
                )
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    'Only JPEG, PNG and WebP images are allowed'
                )
        return value

class GoalSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = [
            'id', 'type', 'type_display', 'description', 'target',
            'deadline', 'completed', 'created_at', 'updated_at',
            'is_owner', 'days_remaining', 'progress'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.user

    def get_days_remaining(self, obj):
        if obj.deadline:
            today = timezone.now().date()
            days = (obj.deadline - today).days
            return max(0, days)
        return None

    def get_progress(self, obj):
        """Calculate the goal progress"""
        return obj.calculate_progress()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password": "Passwords don't match"
            })
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )
            return user
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                if 'username' in str(e).lower():
                    raise serializers.ValidationError({
                        "username": "A user with that username already exists."
                    })
            raise

class UserInfoSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    goals = GoalSerializer(many=True, read_only=True)
    total_workouts = serializers.IntegerField(read_only=True)
    total_calories = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'profile', 'goals',
            'total_workouts', 'total_calories', 'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login']
