from django.utils import timezone

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import EmailAddress
from .settings import rest_email_manager_settings


class EmailAddressViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = EmailAddress.objects.all()
    serializer_class = rest_email_manager_settings.EMAIL_ADDRESS_SERIALIZER

    def get_serializer_class(self):
        if self.action == "verify":
            return rest_email_manager_settings.EMAIL_ADDRESS_KEY_SERIALIZER

        return self.serializer_class

    def perform_create(self, serializer):
        emailaddress = serializer.save(
            user=self.request.user, created_at=timezone.now()
        )
        emailaddress.send_emails(self.request)

    @action(["post"], detail=False)
    def verify(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
