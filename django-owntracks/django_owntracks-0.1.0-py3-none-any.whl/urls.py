from . import views

from django.urls import path

app_name = "owntracks"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("device/<pk>", views.DeviceDetailView.as_view(), name="device-detail"),
    path("waypoint", views.WaypointListView.as_view(), name="waypoint-list"),
    path("waypoint/<pk>", views.WaypointDetailView.as_view(), name="waypoint-detail"),
    path("waypoint/<pk>/download", views.WaypointDownloadView.as_view(), name="waypoint-download",),
    path("waypoint/<pk>/publish", views.WaypointPublishView.as_view(), name="waypoint-publish",),
    path("waypoint/<pk>/qrcode", views.QRView.as_view(), name="waypoint-qrcode"),
]
