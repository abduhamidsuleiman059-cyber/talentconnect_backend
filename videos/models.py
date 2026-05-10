from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q, F


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='videos_profile',
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f'Profile for {self.user.username}'


class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    description = models.TextField(blank=True, null=True)
    card_display_name = models.CharField(
        max_length=150,
        blank=True,
        help_text='Shown as @name on the video card (optional).',
    )
    card_logo = models.ImageField(
        upload_to='video_logos/',
        blank=True,
        null=True,
        help_text='Profile image for this video in the feed.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    @property
    def display_handle(self):
        custom = (self.card_display_name or '').strip()
        if custom:
            return custom
        u = getattr(self, 'user', None)
        if u is not None and getattr(u, 'username', ''):
            return (u.username or '').strip()
        return ''

    @property
    def creator_avatar_url(self):
        """Resolved avatar for the creator rail (card upload, then profile, then None)."""
        if self.card_logo:
            return self.card_logo.url
        try:
            av = self.user.videos_profile.avatar
            if av:
                return av.url
        except ObjectDoesNotExist:
            pass
        return None


class VideoLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='video_likes',
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'video'], name='unique_video_like_per_user'),
        ]

    def __str__(self):
        return f'{self.user_id} likes {self.video_id}'


class VideoComment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='video_comments',
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.text[:40]}'


class CreatorFollow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_relations',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower_relations',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_creator_follow_pair',
            ),
            models.CheckConstraint(
                condition=~Q(follower=F('following')),
                name='creator_follow_no_self',
            ),
        ]

    def __str__(self):
        return f'{self.follower_id} -> {self.following_id}'
