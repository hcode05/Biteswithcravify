from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings

def detectUser(user):
    if user.role == 1:
        return 'vendordashboard'  # name from urls.py
    elif user.role == 2:
        return 'custdashboard'    # name from urls.py
    elif user.role is None and user.is_superadmin:
        return 'admin:index'      # name for Django admin
def send_verification_email(request, user):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('accounts/emails/account_verification_email.html',
                               {
                                'user': user,
                                'domain': current_site,
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'token': default_token_generator.make_token(user),
                               })
    to_email = user.email
    mail = EmailMessage(mail_subject, message,from_email, to=[to_email])
    mail.send()
    
def send_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)
    if(isinstance(context['to_email'], str)):
        to_email = []
        to_email.append(context['to_email'])
    else:
        to_email = context['to_email']
    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    mail.content_subtype = "html"
    mail.send()