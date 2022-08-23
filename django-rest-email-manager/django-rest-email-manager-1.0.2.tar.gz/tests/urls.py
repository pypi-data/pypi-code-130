from django.urls import path, include


urlpatterns = [path("", include("rest_email_manager.urls"))]
