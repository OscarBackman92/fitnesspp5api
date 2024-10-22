from rest_framework import serializers
from .models import UserFollow, WorkoutLike, WorkoutComment
from workouts.serializers import WorkoutSerializer

class UserFollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)

    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'following', 'follower_username', 
                 'following_username', 'created_at']
        read_only_fields = ['created_at']

class WorkoutLikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = WorkoutLike
        fields = ['id', 'user', 'workout', 'username', 'created_at']
        read_only_fields = ['created_at']

class WorkoutCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = WorkoutComment
        fields = ['id', 'user', 'workout', 'content', 'username', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'user']