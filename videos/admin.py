from django.contrib import admin

from .models import CreatorFollow, UserProfile, Video, VideoComment, VideoLike


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'card_display_name',
        'user',
        'view_count',
        'created_at',
        'is_approved',
    )
    list_filter = ('is_approved', 'created_at')
    search_fields = ('title', 'card_display_name', 'user__username')
    ordering = ('-created_at',)


@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video', 'created_at')
    list_filter = ('created_at',)


@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username')


@admin.register(CreatorFollow)
class CreatorFollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'created_at')
    list_filter = ('created_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'avatar')
    search_fields = ('user__username',)
