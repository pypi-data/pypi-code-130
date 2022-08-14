class WrongTypeListError(Exception):
    """Raised when wrong type of iterable was used in List class.
    """
    def __init__(self, message: str = 'Wrong type of iterable. You probably use dictionay istead of Sequence.') -> None:
        super().__init__(message)
