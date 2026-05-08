from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .models import Video
from .forms import ContactForm, CustomUserCreationForm


def home(request):
    return render(request, 'home.html')


def discover(request):
    return render(request, 'discover.html')


def upload_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video = request.FILES.get('video')

        Video.objects.create(
            title=title,
            description=description,
            video_file=video
        )

        return redirect('entertainment')

    return render(request, 'upload.html')


def contact(request):
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'contact.html', {'form': form})


def entertainment(request):
    videos = Video.objects.all().order_by('-created_at')
    return render(request, 'entertainment.html', {'videos': videos})


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('home')

    form.fields['username'].widget.attrs.update({'placeholder': 'Username'})
    form.fields['password'].widget.attrs.update({'placeholder': 'Password'})

    return render(request, 'login.html', {'form': form})


def register(request):
    form = CustomUserCreationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')

    form.fields['username'].widget.attrs.update({'placeholder': 'Username'})
    form.fields['email'].widget.attrs.update({'placeholder': 'Email'})
    form.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
    form.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

    return render(request, 'register.html', {'form': form})