from django.http import HttpResponse
from django.views.decorators.http import require_POST

from swapper import load_model

from notifications.wrappers import NotificationWrapper

Notification = load_model("notification", "Notification")


@require_POST()
def callbacks(request, handler, callback_id, *args, **kwargs):
    handler = NotificationWrapper.get_handler(handler)
    handler.update_status(request, callback_id)
    return HttpResponse(status=200)


@require_POST()
def generic_callbacks(request, handler, *args, **kwargs):
    handler = NotificationWrapper.get_handler(handler)
    handler.update_status(request)
    return HttpResponse(status=200)
