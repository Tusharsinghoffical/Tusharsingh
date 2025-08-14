from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_html_email(subject, template, context, recipient_list):
    """
    Send HTML email using a template
    """
    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list
    )
    email.attach_alternative(html_content, "text/html")
    return email.send()

def send_welcome_email(user):
    """
    Send welcome email to newly registered users
    """
    subject = 'Welcome to GiftNest!'
    template = 'emails/welcome.html'
    context = {
        'user': user
    }
    return send_html_email(subject, template, context, [user.email])

def send_order_confirmation(order):
    """
    Send order confirmation email
    """
    subject = f'Order Confirmation - Order #{order.id}'
    template = 'emails/order_confirmation.html'
    context = {
        'order': order,
        'user': order.user
    }
    recipient_list = [order.email]
    return send_html_email(subject, template, context, recipient_list)

def send_payment_confirmation(order):
    """
    Send payment confirmation email
    """
    subject = f'Payment Confirmation - Order #{order.id}'
    template = 'emails/payment_confirmation.html'
    context = {
        'order': order,
        'user': order.user
    }
    recipient_list = [order.email]
    return send_html_email(subject, template, context, recipient_list)

def send_welcome_email(user):
    """
    Send welcome email to new users
    """
    subject = 'Welcome to GiftNest!'
    template = 'emails/welcome.html'
    context = {
        'user': user
    }
    recipient_list = [user.email]
    return send_html_email(subject, template, context, recipient_list)

def send_password_reset(user, reset_url):
    """
    Send password reset email
    """
    subject = 'Reset Your Password - GiftNest'
    template = 'emails/password_reset.html'
    context = {
        'user': user,
        'reset_url': reset_url
    }
    recipient_list = [user.email]
    return send_html_email(subject, template, context, recipient_list)
