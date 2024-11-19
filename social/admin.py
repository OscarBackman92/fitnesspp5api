from django.contrib import admin
from .models import WorkoutPost, Like, Comment


@admin.register(WorkoutPost)
class WorkoutPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout', 'created_at', 'updated_at']
    search_fields = ['user__username', 'workout__title']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    search_fields = ['user__username', 'post__workout__title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'content', 'created_at', 'updated_at']
    search_fields = ['user__username', 'post__workout__title']
