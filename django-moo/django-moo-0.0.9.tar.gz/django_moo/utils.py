import warnings, datetime, copy, os, copy
from typing import Iterable
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Manager
from django.db.models.query import QuerySet
from django.db.models import Model
from django.http import Http404
from django.db.models.fields import files
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django_moo.moost import get_setting
from django.http import JsonResponse

DEFAULT_PER_PAGE = get_setting().get('DEFAULT_PER_PAGE')
DEFAULT_PAGE_OFFSET = get_setting().get('DEFAULT_PAGE_OFFSET')

def get_apps_name():
    app_ls = [app for app in settings.INSTALLED_APPS if '.' not in app]
    apps_name = list(OrderSet(os.listdir(settings.BASE_DIR)) + OrderSet(app_ls))
    return apps_name

def get_apps_name_path():
    apps_name = get_apps_name()
    apps_path = [os.path.join(settings.BASE_DIR, app_name) for app_name in apps_name]
    return apps_path

def get_project_name():
    return os.environ['DJANGO_SETTINGS_MODULE'].split('.')[0]

def get_apps_module_name():
    return [f"{get_project_name()}.{app_name}" for app_name in get_apps_name()]

def get_objs_all_attr(objs, attr, ls=[]):
    for obj in objs:
        try:
            ls.append(getattr(obj, attr))
        except AttributeError:
            pass
    return ls

def rest_response(value):
    if type(value) == list:
        return JsonResponse(value, safe=False)
    else:
        return JsonResponse(value)

class QuerySetPaginateObject:  # per_page再settings中可以设置
    def __init__(self, query, per_page=DEFAULT_PER_PAGE, index_page=1, orphans=0, allow_empty_first_page=True, page_offset=DEFAULT_PAGE_OFFSET) -> None:
        self.paginator = Paginator(query, per_page, orphans, allow_empty_first_page)
        self.page = self.get_page(index_page)
        self.page_offset = page_offset
        self.index_page = index_page

    def get_page_offset_list(self):
        ls = []
        for index in range(self.index_page-3, self.index_page+4):
            try:
                self.paginator.page(index)
                ls.append(index)
            except EmptyPage:
                pass
        try:
            min_index = self.page_range[0]
            if min_index != ls[0]:
                ls.insert(0, '...')
                ls.insert(0, min_index)
            max_index = self.page_range[-1]
            if max_index != ls[-1]:
                ls.append(0, '...')
                ls.append(max_index)
            return ls
        except IndexError:
            return []

    @property
    def num_pages(self):
        return self.paginator.num_pages
    
    @property
    def page_range(self):
        return self.paginator.page_range

    def get_page(self, index_page):
        try:
            return self.paginator.page(index_page)
        except EmptyPage:
            raise Http404
    
    def get_previous_page_number(self):
        try:
            return self.page.previous_page_number()
        except EmptyPage:
            return None
    
    def get_next_page_number(self):
        try:
            return self.page.next_page_number()
        except EmptyPage:
            return None

    def get_object_list(self):
        return self.page.object_list

    def get_other_message(self):
        context = {}
        context['all_page'] = self.num_pages
        context['next_page'] = self.get_next_page_number()
        context['previous_page'] = self.get_previous_page_number()
        context['page_offset_list'] = self.get_page_offset_list()
        context['current_page'] = self.index_page
        return context
            
class QToDict:
    def __init__(self, q, request, context={}) -> None:
        self.request = request
        self.context = context
        if isinstance(q, Model):
            self.context.update(self.query_to_dict(q))
        if isinstance(q, QuerySet):
            self.context=self.queryset_to_dict(q)
        assert isinstance(q, Model) or isinstance(q, QuerySet), {
            TypeError("please input value type of Model instance or QuerySet.")
        }

    def query_to_dict(self, query, context={}):
        for attr in self.get_query_attrs(query):
            result = getattr(query, attr)
            if callable(result) and not isinstance(result, Model) and not isinstance(result, Manager):
                result = result()
            if isinstance(result, datetime.datetime):
                context[attr] = str(result).split('.')[0]
            elif isinstance(result, datetime.timedelta):
                context[attr] = str(result).split('.')[0]
            elif isinstance(result, datetime.date):
                context[attr] = str(result)
            elif isinstance(result, files.FieldFile):
                if settings.MEDIA_URL.startswith('/') and settings.MEDIA_URL.endswith('/'):
                    context[attr] = f'{self.request.scheme}://{self.request.get_host()}{settings.MEDIA_URL}{str(result)}'
                else:
                    raise ValueError("MEDIA_URL in settings.py must start with '/' and end with '/'.")
            elif isinstance(result, Model):
                # context[attr] = self.query_to_dict(result)
                context[attr] = result.pk
            elif isinstance(result, Manager):
                # context[attr] = self.queryset_to_dict(result.all())
                context[attr] = [item.pk for item in result.all()]
            else:
                context[attr] = result
        return context

    def queryset_to_dict(self, queryset, context=[]):
        return [copy.deepcopy(self.query_to_dict(query)) for query in queryset]

    @classmethod
    def get_query_attrs(cls, query):
        class SampleModel(Model):
            pass
        attrs = OrderSet(dir(query.__class__)) - OrderSet(dir(SampleModel)).remove_('id')
        attrs = cls.filter_attrs(query, attrs)
        return attrs

    @classmethod
    def filter_attrs(cls, query, attrs):
        attrs_set = copy.deepcopy(attrs)
        for attr in attrs:
            try:
                result = getattr(query, attr)
            except ObjectDoesNotExist:
                attrs_set.remove(attr)
                warnings.warn("you cannot get OneToOne field by realted name, because your model exist ForeignKey or ManyToMany field which point to a same model with OneToOne field.")
                continue
            if isinstance(result, datetime.date) or isinstance(result, datetime.datetime):
                attrs_set.remove("get_next_by_"+attr)
                attrs_set.remove("get_previous_by_"+attr)
            if isinstance(result, Model):
                try:
                    attrs_set.remove(attr+"_id")
                except KeyError:
                    pass
        return attrs_set

    def get_result(self):
        return self.context

class OrderSet:
    def __init__(self, iterable:Iterable) -> None:
        if not isinstance(iterable, Iterable):
            t = type(iterable)
            raise TypeError(f"'{t}' object is not iterable.")
        self.iterable = list(iterable)
        self._remove_duplicate()

    def add(self,value):
        self.iterable.append(value)
        self._remove_duplicate()

    def add_(self, value):
        ls = copy.deepcopy(self.iterable)
        ls.append(value)
        return OrderSet(ls)

    def remove(self, value):
        self.iterable = [i for i in self.iterable if i != value]

    def remove_(self, value):
        return OrderSet([i for i in self.iterable if i != value])
    
    def _remove_duplicate(self):
        ls = []
        for i in self.iterable:
            while i not in ls:
                ls.append(i)
        self.iterable = ls

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.iterable})'

    def __repr__(self) -> str:
        return str(self)

    def __add__(self, orderset):
        return OrderSet(self.iterable + orderset.iterable)

    def __sub__(self, orderset):
        ls = copy.deepcopy(self.iterable)
        for i in orderset:
            if i in ls:
                ls.remove(i)
        return OrderSet(ls)

    def __iter__(self):
        return iter(self.iterable)

    def __contains__(self, key):
        return (key in self.iterable)

    def __eq__(self, orderset):
        return self.iterable == orderset.iterable