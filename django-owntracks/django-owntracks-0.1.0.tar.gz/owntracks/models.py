import uuid

from django.conf import settings
from django.db import models
from django.db.models.fields.related import ForeignKey


class Waypoint(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # https://owntracks.org/booklet/tech/json/#_typewaypoint
    rad = models.PositiveIntegerField("radius")
    tst = models.DateTimeField()
    rid = models.CharField("region id", max_length=10)
    lon = models.FloatField("longitude")
    lat = models.FloatField("latitude")
    desc = models.TextField("description")

    # beacon = models.BooleanField(default=False)
    # major = models.PositiveSmallIntegerField(default=0)
    # minor = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-tst"]

    def __str__(self):
        return self.desc


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tid = models.CharField(max_length=2)
    desc = models.TextField()

    def __str__(self):
        return self.desc


class Location(models.Model):
    # https://owntracks.org/booklet/tech/json/#_typelocation
    device = ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    lon = models.FloatField("longitude")
    lat = models.FloatField("latitude")
    extra = models.JSONField()

    class Meta:
        ordering = ["-timestamp"]
