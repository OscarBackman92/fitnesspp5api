from rest_framework import serializers
from .models import Profile
from workouts.models import Workout


class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    workouts_count = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner

    def get_workouts_count(self, obj):
        return Workout.objects.filter(owner=obj.owner).count()

    class Meta:
        model = Profile
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'name',
            'bio', 'image', 'is_owner', 'workouts_count',
            'weight', 'height'
        ]