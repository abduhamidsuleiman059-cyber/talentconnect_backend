from django import forms
from django.core.validators import MinLengthValidator
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Name',
                'class': 'form-control',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your Email',
                'class': 'form-control',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Your Message',
                'class': 'form-control',
                'rows': 5,
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['name'].validators = [MinLengthValidator(2)]
        self.fields['message'].validators = [MinLengthValidator(10)]
        
        # Add custom error messages
        self.fields['name'].error_messages = {
            'required': 'Please enter your name',
            'min_length': 'Name must be at least 2 characters long'
        }
        self.fields['email'].error_messages = {
            'required': 'Please enter your email address',
            'invalid': 'Please enter a valid email address'
        }
        self.fields['message'].error_messages = {
            'required': 'Please enter your message',
            'min_length': 'Message must be at least 10 characters long'
        }