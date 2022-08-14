"""Cauldron provides a simple singleton class."""


class SingletonMixin:
    """
    A base class that provides the function to create singleton objects.
    ```py
    >>> class MySingleton(other_base_classes, SingletonMixin):
    ...    def __init__(self, *args, **kwargs):
    ...        # do stuff here
    ...        ...
    ...
    >>> singleton = MySingleton()
    >>> other_singleton = MySingleton()
    >>> id(singleton) == id(other_singleton)
    True
    ```
    """

    __singleton = None

    def __new__(cls):
        if type(cls) == SingletonMixin:
            raise TypeError("SingletonMixin cannot be directly instantiated")
        if not cls.__singleton:
            cls.__singleton = object.__new__(cls)
        return cls.__singleton
