from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'weight',
                    'height', 'gender', 'created_at', 'updated_at')
    search_fields = ('user__username', 'name')
    list_filter = ('gender',)
    ordering = ('-created_at',)

