# [Standard Library]
from enum import Enum


class ProcessingExecutor(Enum):
    """
    The processing engine to use for a subscriber.
    """

    SAME_THREAD = "SAME_THREAD"
    MULTIPLE_THREADS = "MULTIPLE_THREADS"
    MULTIPLE_PROCESSES = "MULTIPLE_PROCESSES"
