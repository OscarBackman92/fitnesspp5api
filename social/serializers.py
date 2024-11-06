from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserFollow, WorkoutLike, WorkoutComment
from workouts.serializers import WorkoutSerializer

class UserBasicSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']

    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            return str(obj.profile.profile_image)
        return None

class UserFollowSerializer(serializers.ModelSerializer):
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)

    class Meta:
        model = UserFollow
        fields = [
            'id', 'follower', 'following', 'created_at'
        ]
        read_only_fields = ['follower']

class WorkoutLikeSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    workout = WorkoutSerializer(read_only=True)

    class Meta:
        model = WorkoutLike
        fields = [
            'id', 'user', 'workout', 'created_at'
        ]
        read_only_fields = ['user']

class WorkoutCommentSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    workout = WorkoutSerializer(read_only=True)
    
    class Meta:
        model = WorkoutComment
        fields = [
            'id', 'user', 'workout', 'content',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user']