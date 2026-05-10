from django.shortcuts import render, redirect
from .forms import ContactForm

def contact_view(request):
    form = ContactForm()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'contact/contact.html', {'form': form})

from django.core.mail import send_mail
from django.shortcuts import render, redirect

def contact_view(request):

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        send_mail(
            subject=f"New Contact Message from {name}",
            message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=email,
            recipient_list=['abduhamidsuleiman059@gmail.com'],
            fail_silently=False,
        )

        return redirect('contact')

    return render(request, "contact.html")

# Create your views here.
