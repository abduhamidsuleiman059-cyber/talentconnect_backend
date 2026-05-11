from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('discover/', views.discover, name='discover'),
    path('upload/', views.upload_view, name='upload'),
    path('contact/', views.contact, name='contact'),
    path('entertainment/', views.entertainment, name='entertainment'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('api/video/<int:video_id>/like/', views.api_toggle_like, name='api_toggle_like'),
    path(
        'api/video/<int:video_id>/comments/',
        views.api_list_comments,
        name='api_list_comments',
    ),
    path(
        'api/video/<int:video_id>/comment/',
        views.api_add_comment,
        name='api_add_comment',
    ),
    path(
        'api/user/<int:user_id>/follow/',
        views.api_toggle_follow,
        name='api_toggle_follow',
    ),
    path(
        'api/video/<int:video_id>/view/',
        views.api_record_view,
        name='api_record_view',
    ),
]