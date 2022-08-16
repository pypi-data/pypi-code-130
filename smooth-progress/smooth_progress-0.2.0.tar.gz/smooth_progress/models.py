from math import floor
from .exceptions import ProgressBarClosedError

class ProgressBar:
    """The primary class for the ProgressBar. All control operations exist as methods of
    this class. Once the project is more completed, attributes will be hidden and
    available through getter/setter method pairs.
    """
    def __enter__(self: object) -> object:
        return self

    def __exit__(self: object, t, val, tb) -> None:
        del self

    def __init__(self: object, limit: int = 100, show_percent: bool = True) -> None:
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

    def close(self: object) -> bool:
        """Closes the ProgressBar from mutability, displaying its final state before
        interruption.

        Note that a carriage return is executed BEFORE the final display; this ensures
        console outputs such as ^C from a Control+C SIGKILL will be overwritten.
        """
        if self.opened:
            print("\r" + self.state)
            self.opened = False
            return True
        else:
            return False

    def increment(self: object) -> None:
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

    def interrupt(self: object) -> bool:
        """A more forceful version of close(); interrupts the ProgressBar by closing it
        from mutability, without displaying its final state.
        """
        if self.opened:
            self.opened = False
            print("", end="\r", flush=True)
            return True
        else:
            return False

    def open(self: object) -> bool:
        """Resets all progress and opens the ProgressBar to mutability, displaying its
        initial, empty state.
        """
        if self.opened:
            return False
        else:
            self.count = 0
            self.state = f"[{'-'* self.GRANULARITY}]  0/{str(self.limit)}"
            print(self.state, end="\r", flush=True)
            self.opened = True
            return True

    def show(self: object, end: str = "\n") -> None:
        """Display the current state of the bar, with the end character determined by
        the call.

        :param end: The end character, by default a new line. Only control characters
                    are recommended, but any string can be passed.
        """
        print(self.state, end=end, flush=True)

    def __update(self: object, completion: int, percentage: int) -> None:
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