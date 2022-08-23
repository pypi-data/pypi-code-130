from django.urls import path
from . import views

urlpatterns = [
    # A simple test page
    path('status', views.export_status, name='status'),
    path('scheduled/models', views.export_models, name='models'),
    path('models', views.export_models, name='old_models_path'),
    path('manage/app', views.set_app_export, name='set_app_export'),
    path('manage/model', views.set_model_export, name='set_model_export'),
    path('manage/field/update', views.set_field_property, name='update_field'),
    path('manage/field', views.set_field_export, name='set_field_export'),
]
