from django.urls import path
from . import views

app_name = 'medicio'

urlpatterns = [
    path('', views.home, name='home'),
]
