import dataclasses
import typing

from . import api


@dataclasses.dataclass(frozen=True)
class Annotation:
    key: str
    value: typing.Any = None
    inherited: bool = False
    repeatable: bool = False
    stored: bool = True
    targets: typing.Tuple[type] = dataclasses.field(
        default_factory=lambda: (type, object)
    )

    def __call__(self, obj):
        api.annotate(obj, self)

        return obj

    def is_targetted(self, obj) -> bool:
        return isinstance(obj, self.targets)

    def is_compatible(self, annotation) -> bool:
        return dataclasses.replace(self, value=None) == dataclasses.replace(
            annotation, value=None
        )
