import inspect, types
from django.db.models.query import QuerySet
from django.db.models import Model
from django.http import HttpResponse, JsonResponse
from django.http.response import HttpResponseBase
from django.shortcuts import render
from django.shortcuts import redirect
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django_moo.utils import QToDict, OrderSet, rest_response, QuerySetPaginateObject
from django_moo.built.views import django_moo_index, to_officier_page, django_moo_queryset, django_moo_query
from functools import wraps
from django.conf import settings

def controllor(func):
    @wraps(func)
    def deal(request, *args, **kwargs):
        context = func(request, *args, **kwargs)
        _package = inspect.getfile(func).split('\\')[-2]
        template_name = _package + '/' + func.__name__ + ".html"
        if isinstance(context, dict):
            try:
                render(request, template_name, context)
            except TemplateDoesNotExist:
                return HttpResponse(str(context))
        if isinstance(context, QuerySet):
            try:
                return render(request, template_name, {"ones":context})
            except TemplateDoesNotExist:
                index_page = request.GET.get('page', 1)
                query_paginate = QuerySetPaginateObject(context, index_page=int(index_page)).get_object_list()
                message_dict = QuerySetPaginateObject(context, index_page=int(index_page)).get_other_message()
                ones = QToDict(query_paginate, request).get_result()
                try:
                    fields_message = [(field.name, field.verbose_name) for field in context[0]._meta.fields]
                except IndexError:
                    fields_message = []
                ls = []
                for one in ones:
                    c = {}
                    for field_message in fields_message:
                        c[field_message[1]]=one.get(field_message[0])
                    ls.append(c)
                try:
                    d = {'ones': ls, 'title': context[0]._meta.verbose_name_plural}
                except IndexError:
                    d = {'ones':'ls', 'title': 'None'}
                d.update(message_dict)
                return to_officier_page(request, template_name, django_moo_queryset, d)
        if hasattr(context, '_meta') and callable(context):
            if issubclass(context, Model):
                index_page = request.GET.get('page', 1)
                query_paginate = QuerySetPaginateObject(context._base_manager.all(), index_page=int(index_page)).get_object_list()
                message_dict = QuerySetPaginateObject(context._base_manager.all(), index_page=int(index_page)).get_other_message()
                ones = QToDict(query_paginate, request).get_result()
                fields_message = [(field.name, field.verbose_name) for field in context._meta.fields]
                ls = []
                for one in ones:
                    c = {}
                    for field_message in fields_message:
                        c[field_message[1]]=one.get(field_message[0])
                    ls.append(c)
                d = {'ones': ls, 'title': context._meta.verbose_name_plural}
                d.update(message_dict)
                return to_officier_page(request, template_name, django_moo_queryset, d)
        if context is None:
            return to_officier_page(request, template_name, django_moo_index)
        if isinstance(context, HttpResponseBase):
            return context
        if isinstance(context, Model):
            one = QToDict(context, request).get_result()
            fields_message = [(field.name, field.verbose_name) for field in context._meta.fields]
            c = {}
            for field_message in fields_message:
                c[field_message[1]] = one.get(field_message[0])
            d = {'one': c, 'title':context._meta.verbose_name_plural}
            return to_officier_page(request, template_name, django_moo_query, d)
        return HttpResponse(str(context))
    return deal

def rest_controllor(func):
    @wraps(func)
    def deal(request):
        queryset = func(request)
        if queryset is None:
            return JsonResponse([], safe=False)
        elif isinstance(queryset, dict):
            return JsonResponse(queryset)
        elif issubclass(queryset, Model):
            data = QToDict(queryset._default_manager.all(), request).get_result()
            return rest_response(data)
        elif isinstance(queryset, Model) or isinstance(queryset, QuerySet):
            data = QToDict(queryset, request).get_result()
            return rest_response(data)
        elif isinstance(queryset, HttpResponseBase):
            return queryset
        else:
            return JsonResponse(queryset, safe=False)
    return deal

def url_pattern(url_path, isregex=False, **kwargs):  # url_path, isregex, name(template_name)
    def middle(func):
        @wraps(func)
        def inner(request, *args, **innerkwargs):
            result = func(request, *args, **innerkwargs)
            return result
        if not hasattr(url_pattern, "_all_func"):
            url_pattern._all_func = []
        context = {}
        context['url_path'] = url_path
        context['isregex'] = isregex
        context['func'] = func
        context['name'] = kwargs.get('name') or func.__name__
        url_pattern._all_func.append(context)
        return inner
    return middle

def redirect_to(to='/', permanent=False, ispath=True, **kwargs):  # direct_to(index)
    def middle(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            try:
                to = OrderSet(to) + 1
            except UnboundLocalError:
                to = '/'
            result = func(request, *args, **kwargs)
            if result is None:
                return redirect(to, permanent)
            if isinstance(result, HttpResponseBase):
                return result
            if isinstance(to, types.FunctionType):
                if isinstance(result, list) or isinstance(result, tuple):
                    return redirect(to, *result, permanent)
                elif isinstance(result, dict):
                    return redirect(to, permanent, **result)
                else:
                    return redirect(to, result, permanent)
            elif isinstance(to, str):
                if ispath:
                    if "{}" in to:
                        if isinstance(result, list) or isinstance(result, tuple):
                            return redirect(to.format(*result), permanent)
                        elif isinstance(result, dict):
                            return redirect(to.format(**result), permanent)
                        else:
                            return redirect(to.format(result), permanent)
                    else:
                        raise ValueError("you do not need to return any value.")
                else:
                    if isinstance(result, list) or isinstance(result, tuple):
                        return redirect(reverse(to, args=result), permanent)
                    elif isinstance(result, dict):
                        return redirect(reverse(to, kwargs=result), permanent)
                    else:
                        return redirect(reverse(to, args=[result,]), permanent)
            else:
                raise TypeError("'to' only require function or string")
        return inner
    if callable(to):
        return middle(to)  ## inner
    return middle