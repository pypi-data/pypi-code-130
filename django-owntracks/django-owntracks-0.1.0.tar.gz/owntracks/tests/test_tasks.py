from .. import models, tasks
from . import TestCase

from django.contrib.auth.models import User


class WaypointTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="WaypointTest")
        self.date = "2019-11-06T11:42:53.800762+00:00"

    def test_owntracks_waypoints(self):
        tasks.mqtt_waypoints(
            topic="owntracks/WaypointTest/DeviceTest/waypoints",
            device="DeviceTest",
            username="WaypointTest",
            data={
                "_type": "waypoints",
                "waypoints": [
                    {
                        "_type": "waypoint",
                        "tst": 1560375712,
                        "lat": 100.1,
                        "lon": 100.1,
                        "rad": 100,
                        "desc": "test-location",
                        "rid": "",
                    }
                ],
            },
        )
        self.assertCount(models.Waypoint, 1, "Created one waypoint")
        self.assertCount(models.Device, 0, "Created zero devices")

    def test_owntracks_location(self):
        tasks.mqtt_location(
            topic="owntracks/WaypointTest/DeviceTest",
            device="870e7236-8ea1-4518-8da6-8b40039d963d",
            username="WaypointTest",
            data={
                "batt": 100,
                "lon": 100.3543190608404,
                "acc": 65,
                "p": 102.1,
                "bs": 3,
                "vac": 10,
                "lat": 100.1,
                "inregions": ["test-location"],
                "t": "u",
                "conn": "w",
                "tst": 1571049037,
                "alt": 12,
                "_type": "location",
                "tid": "PR",
            },
        )
        self.assertCount(models.Device, 1, "Created 1 devices")
        self.assertCount(models.Location, 1, "Created 1 location")
