import dataclasses
import types
import typing

from . import attributes, models


def decorate(cls: type) -> type:
    orig_init_subclass = (
        cls.__init_subclass__.__func__
        if not isinstance(cls.__init_subclass__, types.BuiltinMethodType)
        else None
    )

    @classmethod
    def init_subclass(subcls, **kwargs):
        if orig_init_subclass is not None:
            orig_init_subclass(subcls, **kwargs)

        annotations = attributes.annotations.setdefault(subcls)

        attributes.annotations.set(
            subcls,
            {
                key: annotation
                for key, annotation in annotations.items()
                if annotation.inherited
            },
        )

        return subcls

    cls.__init_subclass__ = init_subclass


def annotate(
    obj: typing.Any,
    annotation: models.Annotation,
    /,
    *,
    force: bool = False,
    repeat: bool = True,
) -> None:
    if not annotation.is_targetted(obj) and not force:
        raise TypeError(
            f"object with type {type(obj)} not targetted by annotation {annotation!r}"
        )

    if not annotation.stored:
        return obj

    if isinstance(obj, type) and not attributes.annotations.has(obj):
        decorate(obj)

    annotations = attributes.annotations.setdefault(obj)

    if annotation.repeatable and repeat:
        if annotation.key not in annotations:
            annotation = dataclasses.replace(annotation, value=[annotation.value])
        else:
            if not annotations[annotation.key].is_compatible(annotation):
                raise ValueError(
                    "new annotation cannot merge with existing, repeatable annotation due to conflicting options"
                )

            annotation = dataclasses.replace(
                annotation, value=annotations[annotation.key].value + [annotation.value]
            )

    annotations[annotation.key] = annotation
