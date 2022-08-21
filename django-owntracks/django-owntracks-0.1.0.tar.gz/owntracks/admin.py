from . import models

from django.contrib import admin


@admin.register(models.Waypoint)
class WaypointAdmin(admin.ModelAdmin):
    list_display = ("desc", "lon", "lat", "rad", "tst")


@admin.register(models.Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("desc", "pk", "owner", "tid")
    list_filter = (("owner", admin.RelatedOnlyFieldListFilter),)


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "device", "lon", "lat")
    list_filter = ("device",)
    date_hierarchy = "timestamp"
