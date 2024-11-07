from django.contrib import admin
from .models import UserProfile, Goal

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'weight', 'height', 'gender', 'created_at', 'updated_at')
    search_fields = ('user__username', 'name')
    list_filter = ('gender',)
    ordering = ('-created_at',)

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_profile', 'type', 'description', 'target', 'deadline', 'completed', 'created_at', 'updated_at')
    search_fields = ('user_profile__user__username', 'type', 'description')
    list_filter = ('completed', 'type')
    ordering = ('-created_at',)
