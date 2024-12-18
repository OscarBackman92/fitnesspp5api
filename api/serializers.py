from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from django.db import IntegrityError
from cloudinary.utils import cloudinary_url
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    profile_image = serializers.ImageField(required=False)
    age = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    workouts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'name', 'bio', 'weight', 'height',
            'profile_image', 'date_of_birth', 'created_at',
            'updated_at',
            'gender', 'is_owner', 'workouts_count', 'age'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate_bio(self, value):
        from django.utils.html import strip_tags
        value = strip_tags(value).strip()

        if len(value) > 500:
            raise serializers.ValidationError(
                'Bio cannot exceed 500 characters')

        return value

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.user

    def get_profile_image(self, obj):
        """
        Return the Cloudinary profile image URL or the fallback default image.
        """
        try:
            if obj.profile_image and hasattr(obj.profile_image, 'url'):
                # Return the uploaded profile image URL directly
                return obj.profile_image.url
            
            # Fallback to default profile image
            fallback_url, _ = cloudinary_url(
                "default_profile_ylwpgw",
                format="webp",
                transformation=[
                    {'width': 240, 'height': 240, 'crop': 'fill', 'gravity': 'face'},
                    {'quality': 'auto:eco'},
                    {'fetch_format': 'auto'}
                ]
            )
            return fallback_url
        except Exception as e:
            logger.error(f"Error generating profile image URL: {e}")
            return None

    def get_age(self, obj):
        """Calculate age from date_of_birth."""
        if obj.date_of_birth:
            today = timezone.now().date()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (
                    obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None

    def validate_profile_image(self, value):
        if value:
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError(
                    'Image size cannot exceed 2MB')
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    'Only JPEG, PNG and WebP images are allowed')
        return value


class UserInfoSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    total_workouts = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'profile',
            'total_workouts', 'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login']
