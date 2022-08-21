"""Rate limiting primitives."""
import asyncio
import fractions
import functools
import re
from collections import deque
from time import time
from typing import Callable, Coroutine, Generator

RATE_MASK = re.compile('([0-9]+)/([0-9]*)([A-Za-z]+)')
TIME_QUANTITIES = (  # time quantities in the base unit
    ('s', 1),  # one second, the base unit
    ('m', 60),  # one minute
    ('h', 3600),  # one hour
    ('d', 86400),  # one day
)


class Acquirable:
    """Acquirable object interface."""

    async def acquire(self) -> None:
        """Acquire.

        Raises:
            NotImplementedError: if not implemented

        """
        raise NotImplementedError()

    def release(self) -> None:
        """Release.

        Raises:
            NotImplementedError: if not implemented

        """
        raise NotImplementedError()


class AwaitableMixin(Acquirable):
    """Awaitable object.

    This enables the idiom:

    .. highlight:: python
    .. code-block:: python

        await throttle

    as an alternative to:

    .. highlight:: python
    .. code-block:: python

        await throttle.acquire()

    """

    def __await__(self) -> Generator[Coroutine, None, None]:
        """Make object awaitable.

        Returns:
            Generator[Coroutine, None, None]

        """
        return self.acquire().__await__()


class ContextManagerMixin(Acquirable):
    """Context manager.

    This enables the following idiom for acquiring and releasing a
    throttle around a block:

    .. highlight:: python
    .. code-block:: python

        async with throttle:
            <block>

    """

    async def __aenter__(self) -> None:
        """Context entrance."""
        await self.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context exit.

        Args:
            exc_type: exception type
            exc_val: exception value
            exc_tb: exception traceback

        """
        self.release()


class DecoratorMixin(ContextManagerMixin):
    """Coroutine decorator.

    This enables decorating of a coroutine that always need
    acquiring and releasing a throttle:

    .. highlight:: .python
    .. code-block:: python

        @throttle('3/s')
        async def coroutine():
            <block>

    """

    def __call__(self, coroutine: Callable):
        """Make object callable.

        Args:
            coroutine: coroutine

        Returns:
            Coroutine

        """
        @functools.wraps(coroutine)
        async def wrapper(*args, **kwargs):
            async with self:
                return await coroutine(*args, **kwargs)
        return wrapper


class RateMixin:
    """Encapsulation of a rate limiting.

    This enables setting the limiting rate in the following formats:

    - :code:`"{integer limit}/{unit time}"`
    - :code:`"{limit's numerator}/{limit's denominator}{unit time}"`

    Examples of usage:

    - :code:`"1/s"`, :code:`"2/m"`, :code:`"3/h"`, :code:`"4/d"`
    - :code:`"5/second"`, :code:`"6/minute"`, :code:`"7/hour"`, :code:`"8/day"`
    - :code:`"1/3s"`, :code:`"12/37m"`, :code:`"1/5h"`, :code:`"8/3d"`

    """

    __slots__ = ('limit', 'limited_interval', 'factor', 'unit_time')

    def __init__(self, rate: str) -> None:
        """Save rate.

        Args:
            rate: rate

        """
        self.rate = rate

    @property
    def rate(self) -> str:
        """Rate getter.

        Returns:
            str

        """
        return '{numerator}/{denominator}{unit_time}'.format(
            numerator=self.limit.numerator,
            denominator=self.limit.denominator or '',
            unit_time=self.unit_time,
        )

    @rate.setter
    def rate(self, ratevalue: str) -> None:
        """Rate setter.

        Args:
            ratevalue: rate value

        Raises:
            ValueError: invalid rate value

        """
        match = RATE_MASK.match(ratevalue)
        if match is None:
            raise ValueError('Invalid rate value')

        numer, denom, unit_time = match.groups()
        self.unit_time = unit_time
        self.limit = fractions.Fraction(int(numer), int(denom or 1))
        self.limited_interval = self.limit.denominator * self.time_quantity

    @property
    def time_quantity(self) -> int:
        """Quantity of time in base units.

        Returns:
            int

        """
        return dict(TIME_QUANTITIES)[self.unit_time[0].lower()]

    @property
    def period(self) -> float:
        """Period duration.

        Returns:
            float

        """
        return self.limited_interval / self.limit.numerator


class Throttle(AwaitableMixin, DecoratorMixin, RateMixin):
    """Primitive throttle objects.

    A primitive throttle is a synchronization primitive that manages
    an internal counter and has a trace. A primitive throttle is in
    one of two states, 'locked' or 'unlocked'. It is not owned
    by a particular coroutine when locked.

    Each acquire() call:

        i) appends the coroutine to a FIFO queue
        ii) blocks until the throttle is 'locked'
        iii) decrements the counter

    Each release() call:

        i) appends current timestamp at the and of the trace
        ii) increments the counter

    Each locked() call:

        i) removes expired timestamps from the trace
        ii) returns True if the length of the trace
            exceeds the limit or the counter is equal to zero

    Usage:

    .. highlight:: .python
    .. code-block:: python

        throttle = Throttle()
        ...
        await throttle
        try:
            ...
        finally:
            throttle.release()

    Context manager usage:

    .. highlight:: .python
    .. code-block:: python

        throttle = Throttle()
        ...
        async with throttle:
            ...

    Throttle objects can be tested for locking state:

    .. highlight:: .python
    .. code-block:: python

        if not throttle.locked():
            await throttle
        else:
            # throttle is acquired
            ...

    """

    __slots__ = ('_loop', '_waiters', '_trace', '_curvalue', '_bound_value')

    def __init__(self, rate, *, loop=None) -> None:
        """Set helpers.

        Args:
            rate: rate value
            loop: event loop

        """
        super().__init__(rate)
        self._loop = loop or asyncio.get_event_loop()
        self._waiters: deque = deque()
        self._trace: deque = deque(maxlen=self.limit.numerator)
        self._curvalue = self.limit.numerator
        self._bound_value = self.limit.numerator

    def locked(self) -> bool:
        """Return True if throttle can not be acquired immediately.

        Returns:
            bool

        """
        now = time()
        while self._trace and now - self._trace[0] > self.limited_interval:
            self._trace.popleft()
        return len(self._trace) >= self.limit.numerator or self._curvalue == 0

    def remaining_time(self) -> float:
        """Return the remaining time of the 'locked' state.

        Returns:
            float

        """
        if self._trace:
            return time() - self._trace[0]
        return self.limited_interval

    async def acquire(self) -> None:  # noqa: WPS231
        """Acquire a throttle."""
        fut = self._loop.create_future()
        self._waiters.append(fut)

        while True:
            if fut.done():
                self._waiters.remove(fut)
                self._curvalue -= 1
                break
            elif self.locked():
                delay = self.limited_interval - self.remaining_time()
                await asyncio.sleep(delay)
            else:
                for fut in self._waiters:  # noqa: WPS440
                    if not fut.done():
                        fut.set_result(True)  # noqa: WPS220

    def release(self) -> None:
        """Release a throttle.

        Raises:
            ValueError: when Throttle aleready released

        """
        if self._curvalue >= self._bound_value:
            raise ValueError('Throttle released too many times.')
        self._trace.append(time())
        self._curvalue += 1


throttle = Throttle
