from bitsoframework.media.services import MediaService
from bitsoframework.media.settings import Audio


class AudioService(MediaService):
    """
    Service used to manage the lifecycle of the Audio model.
    """

    model_class = Audio
