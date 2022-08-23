# 本文件存放一些有用的代码模板

import io
from django.http import HttpResponse,FileResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse

from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, routers

from .models import GalleryImage
from .custom_storage import MediaStorage
# from django_backend.custom_storages import MediaStorage

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile

def demo_media_storage(request):
    """演示：直接将一个文件存错到s3 storage 中。
        当前环境 保存到 bucket=mtx-default-13-storage, key为media/upload_file_123123
    """    
    media_storage = MediaStorage()
    filename = "demofile1239"
    imagedata = b'123123'
    imageFileObj = InMemoryUploadedFile(io.BytesIO(
                imagedata), "imagefieldname123", filename, "image/jpeg", len(imagedata), "utf-8")
    media_storage.save("upload_file_123123", imageFileObj)
    return JsonResponse({"bucket":media_storage.bucket.name})