from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.core import serializers

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from importlib import import_module


@csrf_exempt
@never_cache
def get_table(request):
    if request.POST is None or len(request.POST) < 1 \
            or len(settings.TABLE_COPY_PASSWORD) < 10 \
            or 'modName' not in request.POST \
            or 'tableName' not in request.POST \
            or 'copyPass' not in request.POST or request.POST['copyPass'] != settings.TABLE_COPY_PASSWORD:
        return HttpResponseBadRequest()

    p = request.POST
    res = {'obj': []}

    models = import_module("%s.models" % p['modName'])
    t = getattr(models, p['tableName'])

    if 'qLimit' in request.POST and 'qOffset' in request.POST:
        offset = int(request.POST['qOffset'])
        limit = int(request.POST['qLimit']) + offset
        cnt = t.objects.all().order_by('-id').count()
        if limit > cnt:
            limit=cnt
        ro = t.objects.all().order_by('-id')[offset:limit]
    elif 'qLimit' in request.POST:
        limit = int(request.POST['qLimit']) + offset
        ro = t.objects.all().order_by('-id')[:limit]
    elif 'qOffset' in request.POST:
        offset = int(request.POST['qOffset'])
        cnt = t.objects.all().order_by('-id').count()
        limit = cnt - offset
        ro = t.objects.all().order_by('-id')[offset:limit]
    else:
        ro = t.objects.all().order_by('-id')

    res['obj'] = serializers.serialize("json", ro)

    res['len'] = len(ro)
    return JsonResponse(res)
