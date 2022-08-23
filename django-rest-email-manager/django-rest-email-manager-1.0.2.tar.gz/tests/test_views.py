import pytest

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.reverse import reverse

from rest_email_manager.serializers import EmailAddressSerializer

pytestmark = pytest.mark.django_db


User = get_user_model()


class TestEmailAddressViewSet:
    @pytest.mark.parametrize(
        "authenticated, status_code",
        [
            pytest.param(True, status.HTTP_201_CREATED),
            pytest.param(False, status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create(
        self, authenticated, status_code, mocker, api_client, user
    ):
        url = reverse("emailaddress-list")

        mock_send_emails = mocker.patch(
            "rest_email_manager.models.EmailAddress.send_emails"
        )

        if authenticated:
            api_client.force_authenticate(user=user)

        data = {"email": "newemail@example.com", "current_password": "secret"}

        response = api_client.post(url, data)
        assert response.status_code == status_code

        if authenticated:
            serializer = EmailAddressSerializer(user.emailaddresses.get())
            assert response.data == serializer.data
            mock_send_emails.assert_called()

    def test_create_no_email(self, authenticated_user, api_client):
        """
        POST
        no email
        fails with email address required
        """
        url = reverse("emailaddress-list")
        data = {"current_password": "secret"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_no_password(self, authenticated_user, api_client):
        """
        POST
        no password
        fails with password required
        """
        url = reverse("emailaddress-list")
        data = {"email": "newemail@example.com"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_wrong_password(self, authenticated_user, api_client):
        """
        POST
        wrong password
        fails
        """
        url = reverse("emailaddress-list")
        data = {"email": "newemail@example.com", "current_password": "wrong"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_duplicate_user_email(
        self, authenticated_user, api_client, user_factory
    ):
        """
        POST
        email belongs to another user account
        fails
        """
        url = reverse("emailaddress-list")
        data = {"email": "newemail@example.com", "current_password": "secret"}

        user_factory(email="newemail@example.com")
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_duplicate_email(
        self, authenticated_user, mocker, api_client, email_address_factory
    ):
        """
        POST
        email has been used to create EmailAddress (but not verified) by
        another user
        creates new EmailAddress and sends verification emails
        """
        url = reverse("emailaddress-list")
        data = {"email": "newemail@example.com", "current_password": "secret"}

        mock_send_emails = mocker.patch(
            "rest_email_manager.models.EmailAddress.send_emails"
        )

        email_address_factory(email="newemail@example.com")
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

        serializer = EmailAddressSerializer(
            authenticated_user.emailaddresses.get()
        )

        assert response.data == serializer.data

        mock_send_emails.assert_called()

    def test_create_already_exists(
        self, authenticated_user, mocker, api_client, email_address_factory
    ):
        """
        POST
        EmailAddress for user and email already exists
        sends another verification emails
        """
        url = reverse("emailaddress-list")
        data = {"email": "newemail@example.com", "current_password": "secret"}

        mock_send_emails = mocker.patch(
            "rest_email_manager.models.EmailAddress.send_emails"
        )

        email_address_factory(
            user=authenticated_user, email="newemail@example.com"
        )
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

        mock_send_emails.assert_called()

    def test_verify(
        self, authenticated_user, api_client, email_address_factory
    ):
        email_address = email_address_factory(user=authenticated_user)
        data = {"key": email_address.key}

        response = api_client.post(reverse("emailaddress-verify"), data)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        authenticated_user.refresh_from_db()
        assert authenticated_user.email == email_address.email

    def test_verify_no_auth(self, api_client, email_address):
        data = {"key": email_address.key}
        response = api_client.post(reverse("emailaddress-verify"), data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_verify_invalid_key(self, authenticated_user, api_client):
        data = {"key": "wrong"}
        response = api_client.post(reverse("emailaddress-verify"), data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_email_taken(
        self, authenticated_user, api_client, user_factory, email_address
    ):
        """
        fail if the verification's email address has already been taken by
        another user
        """
        user_factory(email=email_address.email)
        data = {"key": email_address.key}
        response = api_client.post(reverse("emailaddress-verify"), data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_expired(
        self, authenticated_user, mocker, api_client, email_address
    ):
        """
        fail if verification has expired
        """
        api_client.force_authenticate(user=email_address.user)
        data = {"key": email_address.key}

        mocker.patch(
            "rest_email_manager.models.EmailAddress.is_expired",
            new_callable=mocker.PropertyMock,
            return_value=True,
        )

        response = api_client.post(reverse("emailaddress-verify"), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
