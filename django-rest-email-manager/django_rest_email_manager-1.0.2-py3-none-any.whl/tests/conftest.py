import pytest

from pytest_factoryboy import register

from rest_framework.test import APIClient, APIRequestFactory

from factories import UserFactory, EmailAddressFactory


@pytest.fixture
def api_request():
    return APIRequestFactory().request()


@pytest.fixture
def authenticated_user(api_client, user):
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def api_client():
    return APIClient()


register(UserFactory)
register(EmailAddressFactory)
