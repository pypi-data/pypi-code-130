from datetime import timedelta
from urllib.parse import urlencode

import qrcode
import qrcode.image.svg
from dmqtt.shortcuts import single

from . import models

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.detail import BaseDetailView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "owntracks/home.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["device_list"] = models.Device.objects.all()
        data["waypoint_list"] = models.Waypoint.objects.all()
        data["location_list"] = models.Location.objects.order_by("-timestamp")[:10]
        return data


class DeviceDetailView(LoginRequiredMixin, DetailView):
    model = models.Device

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        start = timezone.now() - timedelta(days=7)
        locations = data["location_list"] = models.Location.objects.filter(
            device=self.get_object(),
            timestamp__gte=start,
        )
        data["waypoint_data"] = list(
            models.Waypoint.objects.values_list("lat", "lon", "rad", "desc")
        )
        data["location_data"] = list(
            locations.values_list("lat", "lon", "timestamp")
        )
        return data


class QRView(LoginRequiredMixin, BaseDetailView):
    model = models.Waypoint

    def get(self, request, *args, **kwargs):
        wp = self.get_object()
        # https://owntracks.org/booklet/tech/qr/
        url = "owntracks:///beacon?" + urlencode(
            {
                "rid": wp.rid,
                "name": wp.desc,
                "tst": wp.tst.timestamp(),
                "lon": wp.lon,
                "lat": wp.lat,
                "rad": wp.rad,
            }
        )
        print(url)
        qr = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage)

        return HttpResponse(qr.to_string(), content_type="image/svg+xml")


class WaypointDetailView(LoginRequiredMixin, DetailView):
    model = models.Waypoint


class WaypointDownloadView(LoginRequiredMixin, DetailView):
    model = models.Waypoint

    def get(self, request, **kwargs):
        wp = self.get_object()
        # https://owntracks.org/booklet/tech/json/#_typewaypoint
        # https://owntracks.org/booklet/features/remoteconfig/
        response = JsonResponse(
            {
                "_type": "configuration",
                "waypoints": [
                    {
                        "_type": "waypoint",
                        "rid": wp.rid,
                        "desc": wp.desc,
                        "tst": wp.tst.timestamp(),
                        "lon": wp.lon,
                        "lat": wp.lat,
                        "rad": wp.rad,
                    }
                    for wp in models.Waypoint.objects.all()
                ],
            }
        )
        response["Content-Disposition"] = f'attachment; filename="{wp.pk}.otrc"'
        return response


class WaypointPublishView(LoginRequiredMixin, DetailView):
    model = models.Waypoint
    # https://owntracks.org/booklet/features/remoteconfig/#configuration-file
    def post(self, request, **kwargs):
        wp = self.get_object()
        messages.success(request, "Published waypoint %s" % wp.desc)
        for device in models.Device.objects.all():
            single(
                f"owntracks/{device.owner.username}/{str(device.id).upper()}/cmd",
                json={
                    "_type": "cmd",
                    "action": "setWaypoints",
                    "waypoints": {
                        "waypoints": [
                            {
                                "_type": "waypoint",
                                "rid": wp.rid,
                                "desc": wp.desc,
                                "tst": wp.tst.timestamp(),
                                "lon": wp.lon,
                                "lat": wp.lat,
                                "rad": wp.rad,
                            }
                        ],
                        "_type": "waypoints",
                    },
                },
            )
        return redirect("owntracks:waypoint-list")


class WaypointListView(LoginRequiredMixin, ListView):
    model = models.Waypoint
