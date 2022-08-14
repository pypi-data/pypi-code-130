# [Standard Library]
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from typing import Dict
from typing import List
from typing import Set
from typing import Union

from .errors import EventNotSupportedError
from .event import Event
from .executor import ProcessingExecutor
from .subscriber import Subscriber


class SameThreadPool:
    def submit(self, fn: Callable, *args, **kwargs) -> None:
        return fn(*args, **kwargs)

    def shutdown(self) -> None:
        pass


class Executor(type):
    _pool = None
    _thread_pool = None
    _process_pool = None
    _channels: Dict[str, "Channel"] = {}

    def __call__(
        cls,
        *args,
        identifier: str = None,
        executor: ProcessingExecutor = ProcessingExecutor.SAME_THREAD,
        workers: Union[int, None] = None,
        **kwargs,
    ):
        """
        Create a new Channel instance.

        Args:
            executor (str, optional): Processing executor type. Defaults to ProcessingExecutor.SAME_THREAD.
            workers (Union[int, None], optional): Worker count (threads or processes). Ignored for ProcessingExecutor.SAME_THREAD. Defaults to None.

        Raises:
            ValueError: Invalid executor type.

        Returns:
            _type_: Channel instance.
        """
        if identifier is None:
            raise ValueError("Channel identifier is required")

        if identifier in cls._channels:
            return cls._channels[identifier]

        channel = super(Executor, cls).__call__(*args, identifier, **kwargs)
        pool: Union[ThreadPoolExecutor, ProcessPoolExecutor, SameThreadPool]
        if executor == ProcessingExecutor.SAME_THREAD:
            if cls._pool is None:
                cls._pool = SameThreadPool()
            pool = cls._pool
        elif executor == ProcessingExecutor.MULTIPLE_THREADS:
            if cls._thread_pool is None:
                cls._thread_pool = ThreadPoolExecutor(max_workers=workers)
            pool = cls._thread_pool
        elif executor == ProcessingExecutor.MULTIPLE_PROCESSES:
            if cls._process_pool is None:
                cls._process_pool = ProcessPoolExecutor(max_workers=workers)
            pool = cls._process_pool
        else:
            raise ValueError("Invalid executor")

        # # Define publish function based on executor pool
        def _execute(subscribers: Set[Subscriber], event: Event) -> None:
            for subscriber in subscribers:
                pool.submit(subscriber._on_update, event)

        channel._execute = _execute

        # register channel
        cls._channels[identifier] = channel
        return channel


class Channel(metaclass=Executor):
    def __init__(self, identifier: str, supported_events: Union[List[Event], None] = None):
        self.identifier = identifier
        self._subscribers: Set[Subscriber] = set()
        self.supported_events = set(supported_events if supported_events else list())
        self._execute = lambda subs, event: None

    def subscribe(self, subscriber: Subscriber) -> None:
        """
        Subscribe a subscriber to this Channel.

        Args:
            subscriber (Subscriber): The subscriber to subscribe.

        Raises:
            ValueError: If the subscriber is not an instance of Subscriber.
        """
        if not isinstance(subscriber, Subscriber):
            raise ValueError("subscriber must be an instance of Subscriber")
        self._subscribers.add(subscriber)

    def unsubscribe(self, subscriber: Subscriber) -> None:
        """
        Unsubscribe a subscriber from this Channel.

        Args:
            subscriber (Subscriber): The subscriber to unsubscribe.
        """
        self._subscribers.remove(subscriber)

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event (Event): The event to publish.

        Raises:
            ValueError: If the event is not an instance of Event.
            EventNotSupportedError: If the event is not supported by this Channel.
        """
        if not isinstance(event, Event):
            raise ValueError("event must be an instance of Event")
        if type(event) not in self.supported_events:
            raise EventNotSupportedError(f"{event._get_name()} is not supported")

        self._execute(self._subscribers, event)
