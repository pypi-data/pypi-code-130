from django.conf import settings
from django.db import models

from .custom_storage import PrivateStorage


class PrivateFileField(models.FileField):
    """字段：私有文件"""
    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        storage = None
        if hasattr(settings, 'AWS_PRIVATE_MEDIA_LOCATION'):
            storage = PrivateStorage()
        super().__init__(verbose_name, name, upload_to, storage, **kwargs)