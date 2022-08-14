from .channel import Channel
from .errors import EventNotSupportedError
from .event import Event
from .executor import ProcessingExecutor
from .subscriber import Subscriber

__all__ = [
    "Event",
    "Channel",
    "Subscriber",
    "EventNotSupportedError",
    "ProcessingExecutor",
]

__version__ = "0.0.1"


def publish(event: Event, channel_id: str) -> None:
    channel = Channel(identifier=channel_id)
    channel.publish(event)
