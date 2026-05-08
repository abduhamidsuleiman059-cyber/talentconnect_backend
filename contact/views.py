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

# Create your views here.
