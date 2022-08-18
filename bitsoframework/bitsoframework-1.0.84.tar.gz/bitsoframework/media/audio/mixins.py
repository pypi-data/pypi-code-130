import simplejson
from django.db.models import SET_NULL, ForeignKey, Model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import (FileUploadParser, FormParser,
                                    MultiPartParser)
from rest_framework.response import Response

from bitsoframework.media.audio.serializers import AudioSerializer
from bitsoframework.media.audio.services import AudioService
from bitsoframework.media.serializers import MediaMetadataSerializer
from bitsoframework.media.settings import Audio
from bitsoframework.media.utils import is_audio


class AudioClipModelMixin(Model):
    audio_clip = ForeignKey(Audio, null=True, blank="true", on_delete=SET_NULL)

    class Meta:
        abstract = True


class AbstractAudioClipViewMixin(object):
    delete_existing_audio_clip = True

    def get_audio_clip_for(self, request, instance):

        serializer = AudioSerializer(instance=instance.audio_clip)

        return Response(serializer.data)

    def create_audio_clip_for(self, request, instance):
        """
        Attach a new audio_clip to the underlying record.
        """

        file = None

        for item in request.data.values():

            if not hasattr(item, "file"):
                continue

            file = item

        if file is None:
            raise ValidationError("A single image file should be uploaded")

        if not is_audio(file.name):
            raise ValidationError("The uploaded file is not a valid audio file")

        metadata = simplejson.loads(request.data.get("metadata")) if "metadata" in request.data else {}

        serializer = MediaMetadataSerializer(data=metadata)
        serializer.is_valid(raise_exception=True)

        service = AudioService()

        params = {}

        if serializer.validated_data:
            params.update(serializer.validated_data)

        if instance.audio_clip and self.delete_existing_audio_clip:
            instance.audio_clip.delete()

        audio_clip = service.create(file=file, **params)

        instance.audio_clip = audio_clip
        instance.save()

        serializer = AudioSerializer(audio_clip)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update_audio_clip_for(self, request, instance):

        service = AudioService()

        serializer = AudioSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if instance.audio_clip:
            service.update(instance.audio_clip, **serializer.validated_data)

        serializer = AudioSerializer(instance.audio_clip)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def remove_audio_clip_for(self, request, instance):

        if instance.audio_clip:
            audio_clip = instance.audio_clip

            instance.audio_clip = None
            instance.save()

            audio_clip.delete()

        return Response(status=status.HTTP_200_OK)


class AudioClipViewMixin(AbstractAudioClipViewMixin):
    @action(detail=False, methods=["get"], url_path="audio_clip")
    def get_audio_clip(self, request):
        """
        Attach a new audio_clip to the underlying record.
        """

        instance = self.get_audio_clip_owner()

        return self.get_audio_clip_for(request, instance)

    @action(detail=False, methods=["put"], url_path="audio_clip/create",
            parser_classes=(FormParser, MultiPartParser, FileUploadParser))
    def create_audio_clip(self, request):
        """
        Attach a new audio_clip to the underlying record.
        """

        instance = self.get_audio_clip_owner()

        return self.create_audio_clip_for(request, instance)

    @action(detail=False, methods=["patch"], url_path="audio_clip/update")
    def update_audio_clip(self, request):
        """
        Update data for an existing audio_clip record. Notice that updating the
        file itself is not supported.
        """

        instance = self.get_audio_clip_owner()

        return self.update_audio_clip_for(request, instance)

    @action(detail=False, methods=["delete"], url_path="audio_clip/destroy")
    def remove_audio_clip(self, request):
        """
        Remove the currently attached audio_clip to the underlying record.
        """

        instance = self.get_audio_clip_owner()

        return self.remove_audio_clip_for(request, instance)


class AudioClipDetailViewMixin(AbstractAudioClipViewMixin):
    @action(detail=True, methods=["get"], url_path="audio_clip")
    def get_audio_clip(self, request, pk):
        """
        Attach a new audio_clip to the underlying record.
        """

        instance = self.get_object()

        return self.get_audio_clip_for(request, instance)

    @action(detail=True, methods=["put"], url_path="audio_clip/create",
            parser_classes=(FormParser, MultiPartParser, FileUploadParser))
    def create_audio_clip(self, request, pk):
        """
        Attach a new audio_clip to the underlying record.
        """

        instance = self.get_object()

        return self.create_audio_clip_for(request, instance)

    @action(detail=True, methods=["patch"], url_path="audio_clip/update")
    def update_audio_clip(self, request, pk):
        """
        Update data for an existing audio_clip record. Notice that updating the
        file itself is not supported.
        """

        instance = self.get_object()

        return self.update_audio_clip_for(request, instance)

    @action(detail=True, methods=["delete"], url_path="audio_clip/destroy")
    def remove_audio_clip(self, request, pk):
        """
        Remove the currently attached audio_clip to the underlying record.
        """

        instance = self.get_object()

        return self.remove_audio_clip_for(request, instance)
