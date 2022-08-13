import datetime
from typing import Callable
from typing import Collection
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

from .clients import Client

Result = Union[str, List[List[int]]]
Runnable = Callable[[], Result]
# Callback = Callable[[], CallbackResult]
# Runnable = Callable[[], Callback]

Day = Literal[0, 1, 2, 3, 4, 5, 6]


class Job:
    def __init__(
        self,
        func: Runnable,
        when: datetime.time,
        period: Optional[datetime.timedelta] = None,
        until: Optional[datetime.time] = None,
        days: Collection[Day] = (0, 1, 2, 3, 4, 5, 6),
    ):
        self.func = func
        self.when = when
        self.period = period
        self.until = until
        self.days = days
        self.next_run = self._schedule()

    def __lt__(self, other) -> bool:
        return self.next_run < other.next_run

    def _schedule(self) -> datetime.datetime:
        next_run = datetime.datetime.now()

        if next_run.time() < self.when:
            next_run = datetime.datetime.combine(next_run.date(), self.when)
        elif self.period is not None:
            next_run += self.period

        # If we've run out of scheduled time for today, advance to tomorrow.
        if (self.period is None and next_run.time() > self.when) or (
            self.until is not None and next_run.time() > self.until
        ):
            tomorrow = next_run.date() + datetime.timedelta(days=1)
            next_run = datetime.datetime.combine(tomorrow, self.when)

        # We may also need to advance to the next available day.
        while next_run.weekday not in self.days:
            next_day = next_run.date() + datetime.timedelta(days=1)
            next_run = datetime.datetime.combine(next_day, self.when)

        return next_run

    def run(self) -> Result:
        result = self.func()
        self.next_run = self._schedule()
        return result


class Schedule:
    def __init__(self):
        self.jobs: List[Job] = []

    def add(
        self,
        func: Runnable,
        when: Optional[datetime.time] = None,
        *,
        period: Optional[datetime.timedelta] = None,
        until: Optional[datetime.time] = None,
        days: Collection[Day] = (0, 1, 2, 3, 4, 5, 6),
    ):
        if when is None:
            when = datetime.time()
        if until is not None and until <= when:
            raise ValueError("'until' must be after 'when'")
        if len(days) < 1:
            raise ValueError("must specify at least one day")

        # if bool(at) != bool(every):
        #     raise ValueError("must specify one of 'at' or 'every'")
        # self.jobs.append(Job(func))

    def run(self, client: Client):
        ...
