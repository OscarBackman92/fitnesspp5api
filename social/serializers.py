from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserFollow, WorkoutLike, WorkoutComment, WorkoutPost
from workouts.models import Workout

class UserFollowSerializer(serializers.ModelSerializer):
    """Serializer for following users."""
    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'following', 'created_at']

class WorkoutLikeSerializer(serializers.ModelSerializer):
    """Serializer for liking workout posts."""
    class Meta:
        model = WorkoutLike
        fields = ['id', 'user', 'workout_post', 'created_at']

class WorkoutCommentSerializer(serializers.ModelSerializer):
    """Serializer for workout comments."""
    user = serializers.StringRelatedField(read_only=True)  # Displaying the username of the user who commented

    class Meta:
        model = WorkoutComment
        fields = ['id', 'user', 'workout_post', 'content', 'created_at', 'updated_at']

class WorkoutPostSerializer(serializers.ModelSerializer):
    """Serializer for shared workouts (WorkoutPost)."""
    workout = serializers.StringRelatedField()  # You can change this to show specific workout data (e.g., name, type)
    user = serializers.StringRelatedField()  # Display username of the user who shared the workout

    class Meta:
        model = WorkoutPost
        fields = ['id', 'workout', 'user', 'shared_at']

class FeedSerializer(WorkoutPostSerializer):
    """Serializer for the social feed showing workout posts."""
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta(WorkoutPostSerializer.Meta):
        fields = WorkoutPostSerializer.Meta.fields + ['has_liked', 'likes_count', 'comments_count']

    def get_has_liked(self, obj):
        """ Checks if the authenticated user has liked this workout post. """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return WorkoutLike.objects.filter(user=request.user, workout_post=obj).exists()
        return False

    def get_likes_count(self, obj):
        """ Returns the number of likes for this workout post. """
        return obj.workout_likes.count()

    def get_comments_count(self, obj):
        """ Returns the number of comments for this workout post. """
        return obj.workout_comments.count()
