from rest_framework import serializers
from django.contrib.auth.models import User
from .models import WorkoutPost, WorkoutLike, WorkoutComment, UserFollow
from workouts.serializers import WorkoutSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image', 'is_following']

    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            return obj.profile.profile_image.url
        return None

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFollow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        return False

class WorkoutPostSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    workout = WorkoutSerializer(read_only=True)
    workout_id = serializers.IntegerField(write_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutPost
        fields = [
            'id', 'user', 'workout', 'workout_id',
            'shared_at', 'likes_count', 'comments_count', 'has_liked'
        ]

    def get_likes_count(self, obj):
        return WorkoutLike.objects.filter(workout=obj.workout).count()

    def get_comments_count(self, obj):
        return WorkoutComment.objects.filter(workout=obj.workout).count()

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return WorkoutLike.objects.filter(
                workout=obj.workout,
                user=request.user
            ).exists()
        return False

class WorkoutCommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = WorkoutComment
        fields = ['id', 'user', 'workout', 'content', 'created_at']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class UserFollowSerializer(serializers.ModelSerializer):
    follower = UserProfileSerializer(read_only=True)
    following = UserProfileSerializer(read_only=True)
    following_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'following', 'following_id', 'created_at']

    def validate_following_id(self, value):
        request = self.context.get('request')
        if request.user.id == value:
            raise serializers.ValidationError("You cannot follow yourself.")
        return value