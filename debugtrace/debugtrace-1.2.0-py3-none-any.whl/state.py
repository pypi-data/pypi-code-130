# state.py
# (C) 2020 Masato Kokubo
__author__  = 'Masato Kokubo <masatokokubo@gmail.com>'

from collections import deque
import datetime

class State(object):
    """
    Have the trace state for a thread

    @since: 1.2.0
    """
    __slots__ = [
        '_thread_id',
        '_nest_level',
        '_previous_nest_level',
        '_previous_line_count',
        '_times',
    ]

    def __init__(self, thread_id: int):
        self._thread_id = thread_id
        self._times = deque()
        self.reset()

    @property
    def thread_id(self) -> int:
        """
        The thread id.
        """
        return self._thread_id

    @property
    def nest_level(self) -> int:
        """
        The nest level.
        """
        return self._nest_level

    @property
    def previous_nest_level(self) -> int:
        """
        The previous nest level.
        """
        return self._previous_nest_level

    @property
    def previous_line_count(self) -> int:
        """
        The previous line count.
        """
        return self._previous_line_count

    @previous_line_count.setter
    def previous_line_count(self, value: int):
        """
        The previous line count.
        """
        self._previous_line_count = value

    def reset(self):
        self._nest_level = 0
        self._previous_nest_level = 0
        self._previous_line_count = 0
        self._times.clear()

    def __str__(self) -> str:
        """
        Returns:
            str: A string representation of this object.
        """
        return '(State){'
        + 'thread_id: ' + self._thread_id
        + ', nest_level: ' + self._nest_level
        + ', previous_nest_level: ' + self._previous_nest_level
        + ', previous_line_count: ' + self._previous_line_count
        + ', times: ' + self._times
        + '}'

    def up_nest(self):
        """
        Ups the nest level.
        """
        self._previous_nest_level = self._nest_level
        if (self._nest_level >= 0):
            self._times.append(datetime.datetime.now())
        self._nest_level += 1

    def down_nest(self) -> datetime.datetime:
        """
        Downs the nest level.
        
        Returns:
            datetime.datetime: The time when the corresponding upNest method was invoked
        """
        self._previous_nest_level = self._nest_level
        self._nest_level -= 1
        return self._times.pop() if len(self._times) > 0 else datetime.datetime.now()
