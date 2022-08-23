import io
from django.http import HttpResponse, FileResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse

from django.shortcuts import render
from rest_framework import serializers, viewsets, routers

from .models import GalleryImage
from .custom_storage import MediaStorage
# from django_backend.custom_storages import MediaStorage

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from mtxauth.permission import MtxJwtPermission
import jwt
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = '__all__'

    # url = serializers.HyperlinkedIdentityField(view_name="user")


class GalleryImageViewSet(viewsets.ModelViewSet):
    # queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [MtxJwtPermission]

    # def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     """
    #     if self.action == 'list':
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        return GalleryImage.objects.all()
    
    def create(self, request):
        print("create image")
        return JsonResponse({"success":True})
        # pass

    # def list(self, request):
    #     queryset = User.objects.all()
    #     serializer = GalleryImageSerializer(queryset, many=True,context={'request': request})
    #     return Response(serializer.data)

@csrf_exempt
def demo_media_storage(request):
    """演示：直接将一个文件存错到s3 storage 中。
        当前环境 保存到 bucket=mtx-default-13-storage, key为media/upload_file_123123
    """
    # b64_image = request.
    media_storage = MediaStorage()
    filename = "demofile1239"
    imagedata = b'123123'
    imageFileObj = InMemoryUploadedFile(io.BytesIO(
        imagedata), "imagefieldname123", filename, "image/jpeg", len(imagedata), "utf-8")
    media_storage.save("upload_file_123123", imageFileObj)
    return JsonResponse({"bucket": media_storage.bucket.name})

@csrf_exempt
def upload_image(request):
    pass
