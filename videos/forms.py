from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from contact.models import Contact


class VideoUploadForm(forms.Form):
    card_display_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Display name (shown as @name on your video)',
                'autocomplete': 'off',
                'class': 'upload-input',
            }
        ),
    )
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'placeholder': 'Caption / title', 'class': 'upload-input'}
        ),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Description (optional)',
                'rows': 4,
                'class': 'upload-textarea',
            }
        ),
    )
    card_logo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'accept': 'image/*', 'class': 'upload-file'}
        ),
    )
    video = forms.FileField(
        widget=forms.FileInput(attrs={'accept': 'video/*', 'class': 'upload-file'}),
    )


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message'}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }