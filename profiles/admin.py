from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'created_at', 'name']
    search_fields = ['owner__username', 'name']
    list_filter = ['created_at']
    ordering = ['-created_at']