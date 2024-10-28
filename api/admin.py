# api/admin.py
from django.contrib import admin
from .models import UserProfile, Goal

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at', 'updated_at')
    search_fields = ('user__username', 'name')
    list_filter = ('created_at',)

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'description', 'target', 'deadline', 'created_at')
    list_filter = ('type', 'deadline', 'created_at')
    search_fields = ('user__username', 'description', 'target')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
