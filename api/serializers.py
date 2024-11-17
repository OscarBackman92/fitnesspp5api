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
    age = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    workouts_count = serializers.IntegerField(read_only=True)
    goals = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'name', 'bio', 'weight', 'height',
            'profile_image', 'date_of_birth', 'created_at', 
            'updated_at', 'gender', 'is_owner', 'workouts_count', 'goals', 'age'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate_bio(self, value):
        from django.utils.html import strip_tags
        value = strip_tags(value).strip()
        
        if len(value) > 500:
            raise serializers.ValidationError('Bio cannot exceed 500 characters')
            
        return value

    def get_goals(self, obj):
        """Get user's goals from the UserProfile."""
        return GoalSerializer(obj.goals.all(), many=True).data

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.user

    def get_profile_image(self, obj):
        if obj.profile_image:
            try:
                url, options = cloudinary_url(
                    str(obj.profile_image),
                    format='webp',
                    transformation=[{'width': 200, 'height': 200, 'crop': 'fill', 'gravity': 'face'}, 
                                    {'quality': 'auto:eco'}, 
                                    {'fetch_format': 'auto'}]
                )
                return url
            except Exception:
                return 'https://res.cloudinary.com/your-cloud-name/image/upload/v1/default_image.png'
        return 'https://res.cloudinary.com/your-cloud-name/image/upload/v1/default_image.png'

    def get_age(self, obj):
        """Calculate age from date_of_birth."""
        if obj.date_of_birth:
            today = timezone.now().date()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None

    def validate_profile_image(self, value):
        if value:
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError('Image size cannot exceed 2MB')
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError('Only JPEG, PNG and WebP images are allowed')
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
        """Calculate the goal progress."""
        return obj.calculate_progress()


class UserInfoSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    goals = GoalSerializer(many=True, read_only=True)
    total_workouts = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'profile', 'goals',
            'total_workouts', 'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login']
