from dmqtt.signals import regex

from . import tasks

# https://owntracks.org/booklet/tech/json/#topics


@regex("^owntracks/(?P<username>[^/]+)/(?P<device>[^/]+)/event$")
def mqtt_event(*, topic, data, match, **kwargs):
    # https://owntracks.org/booklet/tech/json/#_typetransition
    tasks.mqtt_transition.delay(topic=topic, data=data, **match.groupdict())


@regex("^owntracks/(?P<username>[^/]+)/(?P<device>[^/]+)/waypoints$")
def mqtt_waypoints(*, topic, match, data, **kwargs):
    # https://owntracks.org/booklet/tech/json/#_typewaypoint
    tasks.mqtt_waypoints.delay(topic=topic, data=data, **match.groupdict())


@regex("^owntracks/(?P<username>[^/]+)/(?P<device>[^/]+)$")
def mqtt_location(*, topic, match, data, **kwargs):
    try:
        assert data.get("_type") == "location"
    except AssertionError:
        # https://owntracks.org/booklet/tech/json/#_typelwt
        tasks.mqtt_lwt.delay(topic=topic, data=data, **match.groupdict())
    else:
        # https://owntracks.org/booklet/tech/json/#_typelocation
        tasks.mqtt_location.delay(topic=topic, data=data, **match.groupdict())
