from goats.core import metadata
from goats.core import iterables


class Metaclass(type):
    """The type of all quantities."""

    def __new__(mcls, __name, __bases, __dict):
        """"""
        breakpoint()
        mixins = []
        bases = (mcls, *mixins)
        cls = super().__new__(mcls, __name, bases, __dict)
        return cls


class Base:
    """The base class for all quantities."""

    __metadata_attributes__ = None

    def __new__(cls, *args, **kwargs):
        names = cls.__metadata_attributes__
        # Adapt code from metadata.includes
        mixins = []
        return type(cls.__name__, (cls, *mixins), {})


def create(*names: str):
    """Create a base quantity with metadata support."""
    for name in names:
        if name not in metadata.ATTRIBUTES:
            raise ValueError(
                f"Unknown metadata attribute: {name!r}"
            ) from None
    mixins = [
        metadata.ATTRIBUTES[name]['mixin']
        for name in names if name in metadata.ATTRIBUTES
    ]
    _names = [f"_{name}" for name in names]


class Base(iterables.ReprStrMixin):
    """The base class for all quantities."""

    defaults = {
        'unit': '1',
        'name': '',
        'axes': [],
    }

    __metadata_attributes__ = None

    def __init__(self, __interface, **attributes) -> None:
        self.interface = __interface
        self.meta = metadata.OperatorFactory(type(self), *attributes)
        init = {**self.defaults, **attributes}
        for k, v in init.items():
            setattr(self, k, v)

    def __str__(self) -> str:
        attributes = ', '.join(
            f'{k}={getattr(self, k, None)!r}'
            for k in iterables.class_attribute(
                type(self),
                '__metadata_attribute__',
            )
        )
        base = f"{self.interface!r}"
        full = f"{base}, {attributes}" if attributes else base
        return full


# Some thoughts on nomenclature:


class Measurable(metadata.UnitMixin):
    """A quantity with a unit."""


class Identifiable(metadata.NameMixin):
    """A quantity with one or more name(s)."""


class Locatable(metadata.AxesMixin):
    """A quantity with axes."""


class Physical(Measurable, metadata.NameMixin):
    """A quantity with a unit and one or more name(s)."""


class Observable(Physical, metadata.AxesMixin):
    """A quantity with axes, a unit, and one or more name(s)."""


