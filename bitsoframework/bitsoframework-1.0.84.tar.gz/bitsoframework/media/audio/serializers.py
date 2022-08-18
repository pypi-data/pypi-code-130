from bitsoframework.media.serializers import AbstractFileMediaSerializer
from bitsoframework.media.settings import Audio


class AudioSerializer(AbstractFileMediaSerializer):
    class Meta:
        model = Audio
        exclude = ["parent_type", "parent_id", "file"]
