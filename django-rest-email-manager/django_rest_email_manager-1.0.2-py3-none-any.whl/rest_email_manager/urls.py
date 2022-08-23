from rest_framework import routers

from .views import EmailAddressViewSet


router = routers.DefaultRouter()
router.register("emails", EmailAddressViewSet)


urlpatterns = router.urls
