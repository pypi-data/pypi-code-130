import logging
from datetime import datetime, timezone

from celery import shared_task

from . import models

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


def get_or_create_device(*, device, username, **kwargs):
    device, created = models.Device.objects.get_or_create(
        pk=device,
        owner=get_user_model().objects.get(username=username),
        defaults={"tid": kwargs["tid"], "desc": kwargs["tid"]},
    )
    if created:
        logger.info("New device %s", device)
    return device


@shared_task
def mqtt_transition(*, username, device, data, **kwargs):
    # owntracks/user/device/event
    # https://owntracks.org/booklet/tech/json/#_typetransition
    assert data.get("_type") == "transition", "Not a transition event"
    device = get_or_create_device(device=device, username=username, **data)
    print(device, data)


@shared_task
def mqtt_waypoints(*, username, data, **kwargs):
    # owntracks/user/device/waypoints
    # https://owntracks.org/booklet/tech/json/#_typewaypoint
    for w in data["waypoints"]:
        waypoint, created = models.Waypoint.objects.get_or_create(
            tst=datetime.fromtimestamp(w["tst"], tz=timezone.utc),
            lon=w["lon"],
            lat=w["lat"],
            defaults={"rad": w["rad"], "rid": w["rid"], "desc": w["desc"]},
        )
        if created:
            logger.info("Waypoint %s created by %s", waypoint, username)


@shared_task
def mqtt_location(*, username, device, data, **kwargs):
    # owntracks/user/device
    # https://owntracks.org/booklet/tech/json/#_typelocation
    assert data.get("_type") == "location", "Not a location event"
    device = get_or_create_device(device=device, username=username, **data)
    device.location_set.create(
        timestamp=datetime.fromtimestamp(data["tst"], tz=timezone.utc),
        lon=data["lon"],
        lat=data["lat"],
        extra=data,
    )


@shared_task
def mqtt_lwt(*args, **kwargs):
    # https://owntracks.org/booklet/tech/json/#_typelwt
    pass
