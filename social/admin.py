from django.contrib import admin
from .models import WorkoutPost, Like, Comment

@admin.register(WorkoutPost)
class WorkoutPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'workout__workout_type')
    date_hierarchy = 'created_at'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'content')
    date_hierarchy = 'created_at'