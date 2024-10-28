from rest_framework import serializers
from django.contrib.auth.models import User
from cloudinary.utils import cloudinary_url
from .models import UserProfile, Goal
from django.db import IntegrityError

class UserProfileSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    bmi = serializers.FloatField(source='calculate_bmi', read_only=True)
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'weight', 'height', 'fitness_goals', 'date_of_birth', 'age', 'bmi', 'profile_picture', 'created_at', 'updated_at', 'gender']
        read_only_fields = ['created_at', 'updated_at']

    def get_profile_picture(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        else:
            default_image_url, options = cloudinary_url("default_profile_ylwpgw", 
                                                        format="jpg", 
                                                        crop="fill", 
                                                        width=200, 
                                                        height=200)
            return default_image_url

    def update(self, instance, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        if profile_picture:
            instance.profile_picture = profile_picture
        return super().update(instance, validated_data)

class UserRegistrationSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password')
        try:
            user = User.objects.create_user(**validated_data)
            user.set_password(password)
            user.save()
            UserProfile.objects.create(user=user, **profile_data)
            return user
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                if 'username' in str(e).lower():
                    raise serializers.ValidationError({"username": "A user with that username already exists."})
                elif 'email' in str(e).lower():
                    raise serializers.ValidationError({"email": "A user with that email already exists."})
            raise

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['profile'] = UserProfileSerializer(instance.userprofile).data
        return ret

class UserInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    bmi = serializers.FloatField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'name', 'weight', 'height', 'fitness_goals', 
                  'date_of_birth', 'created_at', 'updated_at', 'gender', 'bmi', 'age', 'profile_picture']
        read_only_fields = ['created_at', 'updated_at']

    def get_profile_picture(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        else:
            default_image_url, options = cloudinary_url("default_profile_ylwpgw", 
                                                        format="jpg", 
                                                        crop="fill", 
                                                        width=200, 
                                                        height=200)
            return default_image_url

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['bmi'] = instance.calculate_bmi()
        ret['age'] = instance.age()
        if ret['bmi'] is None:
            ret.pop('bmi')
        if ret['age'] is None:
            ret.pop('age')
        return ret

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'type', 'description', 'target', 'deadline', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

