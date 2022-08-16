class ProgressBarClosedError(Exception):
    """This exception indicates that a call has been made which requires the ProgressBar
    to be open, however the ProgressBar was closed at the time.
    """
    def __eq__(self: object, other: object) -> bool:
        try:
            return self.call == other.call
        except AttributeError:
            return False

    def __init__(self: object, call: str):
        self.call = call
        super().__init__(f"{self.call} was called, but ProgressBar is closed.")