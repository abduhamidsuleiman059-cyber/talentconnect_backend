from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('discover/', views.discover, name='discover'),
    path('upload/', views.upload_view, name='upload'),
    path('contact/', views.contact, name='contact'),
    path('entertainment/', views.entertainment, name='entertainment'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
]