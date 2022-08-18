import django
if django.VERSION >= (4, 0):
    from django.urls import re_path as url, include
else:
    from django.conf.urls import url, include
