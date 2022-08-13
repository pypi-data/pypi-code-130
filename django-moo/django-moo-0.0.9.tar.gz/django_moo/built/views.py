from django.conf import settings as django_settings
from django.template import TemplateDoesNotExist
from django.shortcuts import render

def django_moo_index(request, context={}):
    return render(request, 'django_moo/index.html', context)

def django_moo_queryset(request, context={}):
    return render(request, 'django_moo/queryset.html', context)

def django_moo_query(request, context={}):
    return render(request, 'django_moo/query.html', context)

def to_officier_page(request, template_name, callback, context={}):
    if django_settings.DEBUG:
        try:
            return render(request, template_name, context)
        except TemplateDoesNotExist:
            return callback(request, context)
    else:
        return render(request,template_name, context)