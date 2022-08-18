from django.conf import settings
from django.db import models
from django.db.models.fields.files import FieldFile

from bitsoframework.media.audio.utils import get_duration
from bitsoframework.media.models import AbstractFileMedia
from bitsoframework.media.models import MEDIA_PATH_RESOLVER
from bitsoframework.utils.reflection import exists

THUMBNAIL_ENABLED = getattr(settings, "ORION_IMAGE_THUMBNAIL_ENABLED", exists("easy_thumbnails.models.Source"))
THUMBNAIL_SOURCE_MODEL = getattr(settings, "ORION_IMAGE_THUMBNAIL_SOURCE", "easy_thumbnails.Source")


class AbstractAudio(AbstractFileMedia):
    """
    Model used to map an audio clip uploaded/attached to another model in the system.

    @since: 06/17/2014 20:30:00

    @author: bitsoframework
    """

    type = "audio"
    """
    The unique type of document among the various registered document types.
    """

    file = models.FileField('The audio itself', upload_to=MEDIA_PATH_RESOLVER, max_length=500)
    """
    The audio itself
    """

    duration = models.IntegerField(null=True, blank=True)
    """
    The duration (in seconds) for this entire audio clip.
    """

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        creating = not self.id

        if creating and self.file and not self.duration:
            self.duration = get_duration(self.file.file.file.read())
            self.file.file.file.seek(0)

        super(AbstractAudio, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                        update_fields=update_fields)
