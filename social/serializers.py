from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserFollow, WorkoutLike, WorkoutComment, WorkoutPost
from workouts.serializers import WorkoutSerializer

class UserFollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)

    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'following', 'follower_username', 
                 'following_username', 'created_at']
        read_only_fields = ['follower']

class WorkoutPostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    workout = WorkoutSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutPost
        fields = ['id', 'user', 'workout', 'caption', 'shared_at', 
                 'likes_count', 'comments_count', 'has_liked']

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return WorkoutLike.objects.filter(
                user=request.user,
                workout_post=obj
            ).exists()
        return False

class WorkoutLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WorkoutLike
        fields = ['id', 'user', 'workout_post', 'created_at']
        read_only_fields = ['user']

class WorkoutCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WorkoutComment
        fields = ['id', 'user', 'workout_post', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user']

class FeedSerializer(WorkoutPostSerializer):
    """Extended serializer for feed items with additional engagement data"""
    engagement_rate = serializers.SerializerMethodField()

    class Meta(WorkoutPostSerializer.Meta):
        fields = WorkoutPostSerializer.Meta.fields + ['engagement_rate']

    def get_engagement_rate(self, obj):
        likes = obj.likes.count()
        comments = obj.comments.count()
        total_engagement = likes + comments
        try:
            rate = (total_engagement / obj.user.shared_workouts.count()) * 100
            return round(rate, 2)
        except ZeroDivisionError:
            return 0.0