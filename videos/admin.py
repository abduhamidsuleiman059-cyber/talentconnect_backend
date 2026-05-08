from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)