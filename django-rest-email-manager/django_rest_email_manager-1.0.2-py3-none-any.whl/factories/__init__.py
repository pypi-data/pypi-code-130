import factory

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from faker import Factory as FakerFactory

from rest_email_manager.models import EmailAddress

faker = FakerFactory.create()


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    username = factory.sequence(lambda n: "user{n}".format(n=n))
    email = faker.email()
    password = factory.LazyFunction(lambda: make_password("secret"))

    class Meta:
        model = get_user_model()


class EmailAddressFactory(factory.django.DjangoModelFactory):
    """EmailAddress factory."""

    email = faker.email()
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = EmailAddress
