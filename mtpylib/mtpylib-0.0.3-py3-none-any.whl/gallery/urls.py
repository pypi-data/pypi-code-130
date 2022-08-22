from django.urls import include, path
from . import views
from rest_framework import serializers, viewsets, routers

router = routers.DefaultRouter()
from .views import GalleryImageViewSet
router.register(r'images', GalleryImageViewSet,basename="images")

urlpatterns = [    
    path('', include(router.urls)), # rest_api
    path('demo_media_storage/',views.demo_media_storage)
]
