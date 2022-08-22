"""
Provides definitions and implementations that need to be available to
    all modules that implement graph theory functionality.
"""

__all__ = (
    "NodeNotFoundError",
    "NegativeWeightError",
)


class NegativeWeightError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class NodeNotFoundError(IndexError):
    def __init__(self, message: str):
        super().__init__(message)
