"""Base exceptions and errors for NeuGym"""

__all__ = [
    "NeuGymException",
    "NeuGymError",
    "NeuGymNotImplementedError",
    "NeuGymConnectivityError",
    "NeuGymCheckpointError",
    "NeuGymOverwriteError",
    "NeuGymPermissionError"
]


class NeuGymException(Exception):
    """Base class for exceptions in NeuGym."""


class NeuGymError(NeuGymException):
    """Exception for a serious error in NeuGym."""


class NeuGymNotImplementedError(NeuGymException):
    """Exception raised by functions not implemented."""


class NeuGymConnectivityError(NeuGymException):
    """Exception raised when the connectivity of the world will be illegal."""


class NeuGymCheckpointError(NeuGymException):
    """Exception raised when the state for reset environment is not found."""


class NeuGymOverwriteError(NeuGymException):
    """Exception raised when trying to overwrite something exists without permission."""


class NeuGymPermissionError(NeuGymException):
    """Exception raised when trying to do something not allowed."""

