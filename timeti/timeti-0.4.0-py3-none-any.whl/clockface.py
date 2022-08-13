"""Simple formatter of timestamp."""

from __future__ import annotations

from typing import Union


class Clockface:
    """
    Clock face for timestamp.

    Args:
        timestamp (float): initial timestamp. Default time.time().

    Examples
        >>> Clockface(10)
        0d 0h 0m 10s 0ms

    """

    SPAN_MINUTE = 60
    SPAN_HOUR = 60 * SPAN_MINUTE
    SPAN_DAY = 24 * SPAN_HOUR

    def __init__(self, timestamp: float):
        self.__timestamp = timestamp

    def __add__(self, other: Union[Clockface, float, int]):
        if isinstance(other, (float, int)):
            return Clockface(self.timestamp + other)
        return Clockface(self.timestamp + other.timestamp)

    __radd__ = __add__

    @property
    def timestamp(self):
        """Return timestamp."""
        return self.__timestamp

    @property
    def days(self):
        """Return integer part of days."""
        return round(self.__timestamp // self.SPAN_DAY)

    @property
    def hours(self):
        """Return integer part of hours."""
        return (self.__timestamp - self.days * self.SPAN_DAY) // self.SPAN_HOUR

    @property
    def minutes(self):
        """Return integer part of minutes."""
        return (
            self.__timestamp - self.days * self.SPAN_DAY - self.hours * self.SPAN_HOUR
        ) // self.SPAN_MINUTE

    @property
    def seconds(self):
        """Return integer part of seconds."""
        return int(
            self.__timestamp
            - self.days * self.SPAN_DAY
            - self.hours * self.SPAN_HOUR
            - self.minutes * self.SPAN_MINUTE
        )

    @property
    def milliseconds(self):
        """Return integer part of milliseconds."""
        return int(1_000 * (self.__timestamp - int(self.__timestamp)))

    def __str__(self):
        """Return short clock face view."""
        if self.days > 0:
            return f"{self.days} days {self.hours} hours"

        elif self.hours > 0:
            return f"{self.hours} hours {self.minutes} min"

        elif self.minutes > 0:
            return f"{self.minutes} min {self.seconds} sec"

        elif self.seconds > 0:
            return f"{self.seconds} sec {self.milliseconds} ms"

        else:
            return f"{self.milliseconds} ms"

    def __repr__(self):
        """Return full clock face view."""
        return (
            f"{self.days}d "
            f"{self.hours}h "
            f"{self.minutes}m "
            f"{self.seconds}s "
            f"{self.milliseconds}ms"
        )


if __name__ == "__main__":
    import doctest

    print(doctest.testmod())
