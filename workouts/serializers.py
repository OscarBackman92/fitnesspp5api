from rest_framework import serializers
from .models import Workout, WorkoutComment, WorkoutLike
from django.contrib.humanize.templatetags.humanize import naturaltime

class WorkoutSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
    like_id = serializers.SerializerMethodField()
    comments_count = serializers.ReadOnlyField()
    likes_count = serializers.ReadOnlyField()
    workout_type_display = serializers.CharField(
        source='get_workout_type_display',
        read_only=True
    )

    def validate_image(self, value):
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('Image size larger than 2MB!')
        if value.image.height > 4096:
            raise serializers.ValidationError(
                'Image height larger than 4096px!'
            )
        if value.image.width > 4096:
            raise serializers.ValidationError(
                'Image width larger than 4096px!'
            )
        return value

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner

    def get_like_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            like = WorkoutLike.objects.filter(
                owner=user, workout=obj
            ).first()
            return like.id if like else None
        return None

    class Meta:
        model = Workout
        fields = [
            'id', 'owner', 'is_owner', 'profile_id',
            'profile_image', 'created_at', 'updated_at',
            'title', 'description', 'image', 'workout_type',
            'workout_type_display', 'duration', 'like_id',
            'likes_count', 'comments_count',
        ]

class WorkoutCommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner

    def get_created_at(self, obj):
        return naturaltime(obj.created_at)

    def get_updated_at(self, obj):
        return naturaltime(obj.updated_at)

    class Meta:
        model = WorkoutComment
        fields = [
            'id', 'owner', 'is_owner', 'profile_id', 'profile_image',
            'workout', 'created_at', 'updated_at', 'content'
        ]

class WorkoutCommentDetailSerializer(WorkoutCommentSerializer):
    workout = serializers.ReadOnlyField(source='workout.id')