import json
from functools import wraps

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from django.urls import reverse

from .forms import ContactForm, CustomUserCreationForm, VideoUploadForm
from .models import CreatorFollow, UserProfile, Video, VideoComment, VideoLike


def api_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentication required', 'login_required': True},
                status=401,
            )
        return view_func(request, *args, **kwargs)

    return wrapper


def home(request):
    return render(request, 'home.html')


def discover(request):
    return render(request, 'discover.html')


@login_required
def upload_view(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            card_logo = form.cleaned_data.get('card_logo')
            desc = (form.cleaned_data.get('description') or '').strip()
            Video.objects.create(
                user=request.user,
                title=form.cleaned_data['title'].strip(),
                description=desc or None,
                card_display_name=(form.cleaned_data.get('card_display_name') or '').strip(),
                card_logo=card_logo,
                video_file=form.cleaned_data['video'],
            )
            if card_logo:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.avatar = card_logo
                profile.save(update_fields=['avatar'])
            return redirect('entertainment')
    else:
        form = VideoUploadForm()

    return render(request, 'upload.html', {'form': form})




def contact(request):
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'contact.html', {'form': form})


def entertainment(request):
    base = Video.objects.select_related('user')

    if request.user.is_authenticated:
        videos = base.annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True),
            is_liked=Exists(
                VideoLike.objects.filter(video=OuterRef('pk'), user=request.user)
            ),
            is_following=Exists(
                CreatorFollow.objects.filter(
                    following=OuterRef('user_id'),
                    follower=request.user,
                )
            ),
        ).order_by('-created_at')
    else:
        videos = base.annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True),
            is_liked=Value(False, output_field=BooleanField()),
            is_following=Value(False, output_field=BooleanField()),
        ).order_by('-created_at')

    scroll_to = request.GET.get('v')
    return render(
        request,
        'Entertainment.html',
        {
            'videos': videos,
            'scroll_to_video_id': scroll_to,
        },
    )


@api_login_required
@require_POST
def api_toggle_like(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    like, created = VideoLike.objects.get_or_create(user=request.user, video=video)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    count = VideoLike.objects.filter(video=video).count()
    return JsonResponse({'liked': liked, 'like_count': count})


@require_GET
def api_list_comments(request, video_id):
    get_object_or_404(Video, pk=video_id)
    comments = (
        VideoComment.objects.filter(video_id=video_id)
        .select_related('user')
        .order_by('-created_at')
    )
    payload = [
        {
            'id': c.id,
            'username': c.user.username,
            'text': c.text,
            'created_at': c.created_at.isoformat(),
        }
        for c in comments
    ]
    return JsonResponse({'comments': payload})


@api_login_required
@require_POST
def api_add_comment(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    try:
        data = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    text = (data.get('text') or '').strip()
    if not text:
        return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
    comment = VideoComment.objects.create(
        user=request.user,
        video=video,
        text=text[:2000],
    )
    return JsonResponse(
        {
            'comment': {
                'id': comment.id,
                'username': comment.user.username,
                'text': comment.text,
                'created_at': comment.created_at.isoformat(),
            },
            'comment_count': VideoComment.objects.filter(video=video).count(),
        }
    )


@api_login_required
@require_POST
def api_toggle_follow(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target.id == request.user.id:
        return JsonResponse({'error': 'You cannot follow yourself'}, status=400)
    rel, created = CreatorFollow.objects.get_or_create(
        follower=request.user,
        following=target,
    )
    if not created:
        rel.delete()
        following = False
    else:
        following = True
    return JsonResponse({'following': following})


@require_POST
def api_record_view(request, video_id):
    get_object_or_404(Video, pk=video_id)
    key = 'viewed_video_ids'
    viewed = request.session.get(key, [])
    vid_key = str(video_id)
    if vid_key in viewed:
        video = Video.objects.get(pk=video_id)
        return JsonResponse(
            {'incremented': False, 'view_count': video.view_count},
        )
    viewed = list(viewed) + [vid_key]
    request.session[key] = viewed
    request.session.modified = True
    Video.objects.filter(pk=video_id).update(view_count=F('view_count') + 1)
    video = Video.objects.get(pk=video_id)
    return JsonResponse({'incremented': True, 'view_count': video.view_count})
