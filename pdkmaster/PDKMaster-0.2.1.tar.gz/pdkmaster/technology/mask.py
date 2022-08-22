# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
import abc
from typing import Iterable, Optional

from ..typing import OptSingleOrMulti, SingleOrMulti
from .. import _util
from . import rule as rle, property_ as prp


__all__ = ["DesignMask"]


class _MaskProperty(prp.Property):
    def __init__(self, *, mask: "_Mask", name: str):
        super().__init__(mask.name + "." + name)
        self.mask = mask
        self.prop_name = name


class _DualMaskProperty(prp.Property):
    def __init__(self, *, mask1: "_Mask", mask2: "_Mask", name: str, commutative: bool):
        if commutative:
            supername = f"{name}({mask1.name},{mask2.name})"
        else:
            supername = f"{mask1.name}.{name}({mask2.name})"
        super().__init__(name=supername)

        self.mask1 = mask1
        self.mask2 = mask2
        self.prop_name = name


class _DualMaskEnclosureProperty(prp.EnclosureProperty):
    def __init__(self, *, mask1: "_Mask", mask2: "_Mask", name: str):
        super().__init__(name=f"{mask1.name}.{name}({mask2.name})")

        self.mask1 = mask1
        self.mask2 = mask2
        self.prop_name = name


class _AsymmetricDualMaskProperty(_DualMaskProperty):
    @classmethod
    def cast(cls, value):
        if not (_util.is_iterable(value)):
            raise TypeError("property value has to be iterable of float of length 2")
        value = tuple(_util.i2f(v) for v in value)
        if not ((len(value) == 2) and all(isinstance(v, float) for v in value)):
            raise TypeError("property value has to be iterable of float of length 2")

        return value


class _MultiMaskCondition(prp._Condition, abc.ABC):
    operation = abc.abstractproperty()

    def __init__(self, *, mask: "_Mask", others: SingleOrMulti["_Mask"].T):
        if not isinstance(self.operation, str):
            raise AttributeError("operation _MultMaskCondition abstract attribute has to be a string")
        others = _util.v2t(others)
        super().__init__((mask, others))

        self.mask = mask
        self.others = others

    def __hash__(self):
        return hash((self.mask, *self.others))

    def __repr__(self):
        return "{}.{}({})".format(
            str(self.mask), self.operation,
            ",".join(str(mask) for mask in self.others),
        )


class _InsideCondition(_MultiMaskCondition):
    operation = "is_inside"
class _OutsideCondition(_MultiMaskCondition):
    operation = "is_outside"


class _Mask(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *, name: str):
        self.name = name
        self.width = _MaskProperty(mask=self, name="width")
        self.length = _MaskProperty(mask=self, name="length")
        self.space = _MaskProperty(mask=self, name="space")
        self.area = _MaskProperty(mask=self, name="area")
        self.density = _MaskProperty(mask=self, name="density")

    def __repr__(self):
        return self.name

    def extend_over(self, other: "_Mask"):
        return _DualMaskProperty(mask1=self, mask2=other, name="extend_over", commutative=False)

    def enclosed_by(self, other: "_Mask"):
        return _DualMaskEnclosureProperty(mask1=self, mask2=other, name="enclosed_by")

    def is_inside(self, other: SingleOrMulti["_Mask"].T, *others: "_Mask"):
        masks = (*_util.v2t(other), *others)
        
        return _InsideCondition(mask=self, others=masks)

    def is_outside(self, other: SingleOrMulti["_Mask"].T, *others: "_Mask"):
        masks = (*_util.v2t(other), *others)
        
        return _OutsideCondition(mask=self, others=masks)

    def parts_with(self, condition: SingleOrMulti[prp._BinaryPropertyCondition].T):
        return _PartsWith(mask=self, condition=condition)

    def remove(self, what: "_Mask"):
        return _MaskRemove(from_=self, what=what)

    def alias(self, name: str):
        return _MaskAlias(name=name, mask=self)

    @abc.abstractproperty
    def designmasks(self) -> Iterable["DesignMask"]:
        return tuple()


class DesignMask(_Mask, rle._Rule):
    def __init__(self, *, name: str, fill_space: str):
        super().__init__(name=name)

        if not fill_space in ("no", "same_net", "yes"):
            raise ValueError("fill_space has to be one of ('no', 'same_net', 'yes')")
        self.fill_space = fill_space

        self.grid = _MaskProperty(mask=self, name="grid")

    def __repr__(self):
        return f"design({self.name})"

    def __hash__(self):
        return hash(self.name)

    @property
    def designmasks(self):
        return (self,)


class _PartsWith(_Mask):
    def __init__(self, *,
        mask: _Mask, condition: SingleOrMulti[prp._BinaryPropertyCondition].T,
    ):
        self.mask = mask

        condition = _util.v2t(condition)
        if not all(
            (
                isinstance(cond.left, _MaskProperty)
                and cond.left.mask == mask
            ) for cond in condition
        ):
            raise TypeError(
                "condition has to a single or an iterable of condition on properties of mask '{}'".format(
                    mask.name,
                ))
        self.condition = condition

        super().__init__(name="{}.parts_with({})".format(
            mask.name, ",".join(str(cond) for cond in condition),
        ))

    @property
    def designmasks(self):
        return self.mask.designmasks


class Join(_Mask):
    def __init__(self, masks: SingleOrMulti[_Mask].T):
        self.masks = masks = _util.v2t(masks)

        super().__init__(name="join({})".format(",".join(mask.name for mask in masks)))

    @property
    def designmasks(self):
        for mask in self.masks:
            yield from mask.designmasks


class Intersect(_Mask):
    def __init__(self, masks: SingleOrMulti[_Mask].T):
        self.masks = masks = _util.v2t(masks)

        super().__init__(name="intersect({})".format(",".join(mask.name for mask in masks)))

    @property
    def designmasks(self):
        for mask in self.masks:
            yield from mask.designmasks


class _MaskRemove(_Mask):
    def __init__(self, *, from_: _Mask, what: _Mask):
        super().__init__(name=f"{from_.name}.remove({what.name})")
        self.from_ = from_
        self.what = what

    @property
    def designmasks(self):
        for mask in (self.from_, self.what):
            yield from mask.designmasks


class _MaskAlias(_Mask, rle._Rule):
    def __init__(self, *, name: str, mask: _Mask):
        self.mask = mask

        super().__init__(name=name)

    def __hash__(self):
        return hash((self.name, self.mask))

    def __repr__(self):
        return f"{self.mask.name}.alias({self.name})"

    @property
    def designmasks(self):
        return self.mask.designmasks


class Spacing(_DualMaskProperty):
    def __init__(self, mask1: _Mask, mask2: _Mask):
        super().__init__(mask1=mask1, mask2=mask2, name="space", commutative=True)


class OverlapWidth(_DualMaskProperty):
    def __init__(self, mask1: _Mask, mask2: _Mask):
        super().__init__(mask1=mask1, mask2=mask2, name="overlapwidth", commutative=True)


class Connect(rle._Rule):
    def __init__(self,
        mask1: SingleOrMulti[_Mask].T, mask2: SingleOrMulti[_Mask].T,
    ):
        self.mask1 = mask1 = _util.v2t(mask1)
        self.mask2 = mask2 = _util.v2t(mask2)

    def __hash__(self):
        return hash((self.mask1, self.mask2))

    def __repr__(self):
        s1 = self.mask1[0].name if len(self.mask1) == 1 else "({})".format(
            ",".join(m.name for m in self.mask1)
        )
        s2 = self.mask2[0].name if len(self.mask2) == 1 else "({})".format(
            ",".join(m.name for m in self.mask2)
        )
        return f"connect({s1},{s2})"


class SameNet(_Mask):
    def __init__(self, mask: _Mask):
        if not isinstance(mask, _Mask):
            raise TypeError("mask has to be of type _Mask")
        self.mask = mask

        super().__init__(name=f"same_net({mask.name})")

    @property
    def designmasks(self):
        return self.mask.designmasks
