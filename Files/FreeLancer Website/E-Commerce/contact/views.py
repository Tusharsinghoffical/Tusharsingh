from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            
            # Send email notification
            try:
                send_mail(
                    f'New Contact Form Submission: {contact.subject}',
                    f'''
                    Name: {contact.name}
                    Email: {contact.email}
                    Phone: {contact.phone}
                    Subject: {contact.subject}
                    Message: {contact.message}
                    ''',
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
            except:
                pass
            
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact:contact')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact.html', {'form': form}) 