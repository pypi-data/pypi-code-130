from ..l0.EventOrSituation import EventOrSituation
from ..ns import *
from ..ti.TimeIndexedEvent import TimeIndexedEvent


class Event(TimeIndexedEvent, EventOrSituation):
    __type__ = CPEV["Event"]
