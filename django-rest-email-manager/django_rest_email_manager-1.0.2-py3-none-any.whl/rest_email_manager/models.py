from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils import timezone

from .settings import rest_email_manager_settings


User = get_user_model()


def generate_key():
    return get_random_string(64).lower()


class EmailAddress(models.Model):
    email = models.EmailField()
    user = models.ForeignKey(
        User, related_name="emailaddresses", on_delete=models.CASCADE
    )
    key = models.CharField(max_length=255, default=generate_key)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["email", "user"]

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(days=1)

    def verify(self):
        self.user.email = self.email
        self.user.save()

    def send_emails(self, request):
        self.send_verification_email(request)
        self.send_notification_email(request)

    def send_verification_email(self, request):
        verification_url = rest_email_manager_settings.EMAIL_VERIFICATION_URL
        context = {
            "user": self.user,
            "new_email": self.email,
            "verification_url": verification_url.format(key=self.key),
        }
        to = [self.email]
        rest_email_manager_settings.SEND_VERIFICATION_EMAIL(
            request, context, to
        )

    def send_notification_email(self, request):
        context = {
            "user": self.user,
            "new_email": self.email,
        }
        to = [self.user.email]
        rest_email_manager_settings.SEND_NOTIFICATION_EMAIL(
            request, context, to
        )
