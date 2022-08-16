from math import floor
from typing import NoReturn
from .exceptions import ProgressBarClosedError

class ProgressBar:
    """The primary class for the ProgressBar. All control operations exist as methods of
    this class. Once the project is more completed, attributes will be hidden and
    available through getter/setter method pairs.
    """
    def __enter__(self: object):
        return self

    def __exit__(self: object, t, val, tb):
        del self

    def __init__(self: object, limit: int = 100, show_percent: bool = True):
        """
        :param limit: int, optional, default 100.
        :param show_percent: bool, optional, default True.
        """
        self.count = None
        self.GRANULARITY = 50
        self.limit = limit
        self.opened = False
        self.show_percent = show_percent
        self.state = None

    def close(self: object) -> NoReturn:
        """Closes the ProgressBar from mutability, displaying its final state before
        interruption.

        Note that a carriage return is executed BEFORE the final display; this ensures
        console outputs such as ^C from a Control+C SIGKILL will be overwritten.
        """
        if self.opened:
            print("\r" + self.state)
            self.opened = False

    def increment(self: object) -> NoReturn:
        """Increments the progress and updates the display to reflect the new value. If
        this incrementation takes the progress to the pre-defined limit, closes the
        ProgressBar from mutability.
        """
        if self.opened:
            self.count += 1
            fraction = self.count/self.limit
            self.__update(floor(fraction*self.GRANULARITY), floor(fraction*100))
            print(self.state, end="\r", flush=True)
            if self.count == self.limit:
                self.close()
        else:
            raise ProgressBarClosedError(".increment()")

    def interrupt(self: object) -> NoReturn:
        """A more forceful version of close(); interrupts the ProgressBar by closing it
        from mutability, without displaying its final state.
        """
        self.opened = False

    def open(self: object) -> NoReturn:
        """Resets all progress and opens the ProgressBar to mutability, displaying its
        initial, empty state.
        """
        if not self.opened:
            self.count = 0
            self.state = f"[{'-'* self.GRANULARITY}]  0/{str(self.limit)}"
            print(self.state, end="\r", flush=True)
            self.opened = True

    def __update(self: object, completion: int, percentage: int) -> NoReturn:
        """Hidden method to update the state of the bar with new values. Should only be
        called from within the class itself.

        :param completion: int
        :param percentage: int
        """
        self.state = (
            f"[{'#' * completion}{'-' * (self.GRANULARITY - completion)}]"
            + f"  {str(self.count)}/{str(self.limit)}"
            + (f" [{percentage}%]" if self.show_percent else "")
        )