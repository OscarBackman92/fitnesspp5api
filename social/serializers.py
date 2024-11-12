# social/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserFollow, WorkoutLike, WorkoutComment
from workouts.serializers import WorkoutSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile']

class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'following', 'created_at']

class WorkoutLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLike
        fields = ['id', 'user', 'workout', 'created_at']

class WorkoutCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WorkoutComment
        fields = ['id', 'user', 'workout', 'content', 'created_at']

class FeedSerializer(WorkoutSerializer):
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta(WorkoutSerializer.Meta):
        fields = WorkoutSerializer.Meta.fields + [
            'has_liked', 'likes_count', 'comments_count'
        ]

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return WorkoutLike.objects.filter(
                user=request.user, 
                workout=obj
            ).exists()
        return False

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()