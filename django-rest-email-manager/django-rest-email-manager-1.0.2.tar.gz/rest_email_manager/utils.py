from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_email(subject, template_name, context, to):
    message = render_to_string(context=context, template_name=template_name)
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        to,
    )


def send_verification_email(request, context, to):
    subject = "Confirm Email Change"
    template_name = "rest_email_manager/emails/verify_email.txt"
    send_email(subject, template_name, context, to)


def send_notification_email(request, context, to):
    subject = "Account Email Change"
    template_name = "rest_email_manager/emails/email_update_notification.txt"
    send_email(subject, template_name, context, to)
