from django.test import Client
from django.urls import reverse
from django.utils import timezone

import pytest
from events import models

from .conftest import *


@pytest.mark.django_db
class TestEventView:
    """
    Test case for the Event app views
    """

    @pytest.fixture
    def event_instance(self):
        return models.Event.objects.create(
            title="Event",
            slug="event",
            start_at=timezone.now(),
            is_published=True,
            publish_at=timezone.now() - timezone.timedelta(hours=1),
        )

    def test_event_detail(self, event_instance):
        """
        Test the detail view returns the correct status code
        """

        client = Client()
        event = event_instance
        response = client.get(reverse("events:detail", kwargs={"slug": event.slug}))
        assert response.status_code == 200

    def test_event_index(self):
        """
        Test the index view returns the correct status code
        """
        client = Client()
        response = client.get(reverse("events:index"))
        assert response.status_code == 200

    def test_unpublished_returns_404(self, unpublished_event):
        """
        Test to check that an unpublished event returns a 404
        """
        client = Client()
        response = client.get(
            reverse("events:detail", kwargs={"slug": unpublished_event.slug})
        )

        assert response.status_code == 404

    def test_update_context(self, event_instance):
        """
        Test the context update returns published events queryset
        """
        client = Client()
        event = event_instance
        response = client.get(reverse("events:index"))

        assert event in response.context["object_list"]
        assert event in models.Event.objects.published()
