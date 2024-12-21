from rest_framework import serializers
from django.contrib.auth.models import User
from .models import WorkoutPost, Comment, Like
from workouts.serializers import WorkoutSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data in social interactions."""
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']

    def get_profile_image(self, obj):
        """Get the profile image URL if it exists."""
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            return str(obj.profile.profile_image)
        return None


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for workout post comments."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'post', 'content',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'post']


class WorkoutPostSerializer(serializers.ModelSerializer):
    """Serializer for workout posts with related data."""
    user = UserSerializer(read_only=True)
    workout = WorkoutSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    latest_comments = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutPost
        fields = [
            'id', 'user', 'workout', 'created_at',
            'updated_at', 'likes_count', 'comments_count',
            'has_liked', 'latest_comments'
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_latest_comments(self, obj):
        latest = obj.comments.select_related('user')[:3]
        return CommentSerializer(latest, many=True).data
