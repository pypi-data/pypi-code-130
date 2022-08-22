# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from ..technology import geometry as geo


class ShapeDispatcher:
    """Dispatch to call method based on type of _Shape subclass.

    One can implement execution of code for a certain class by overloading
    the method with the name of the class in a child class.
    By default the methods will call the dispatcher for the super class if not
    overloaded. 
    For multi-inheritance each of the super classes methods will be tried in order.
    The dispatched for the base '_Shape' class will raise NotImplementedError if
    not overloaded.
    """
    def __call__(self, shape: geo._Shape, *args, **kwargs):
        if isinstance(shape, geo.MultiPartShape._Part):
            classname = "MultiPartShape__Part"
        else:
            classname = shape.__class__.__name__.split(".")[-1]
        return getattr(self, classname, self._pd_unhandled)(shape, *args, **kwargs)

    def _pd_unhandled(self, shape: geo._Shape, *args, **kwargs):
        raise RuntimeError(
            "Internal error: unhandled dispatcher for object of type "
            f"{shape.__class__.__name__}"
        )

    def _Shape(self, shape: geo._Shape, *args, **kwargs):
        """This for the base class and by default raises NotImplementedError
        """
        raise NotImplementedError(
            f"No dispatcher implemented for object of type {shape.__class__.__name__}"
        )

    _Rectangular = _pd_unhandled
    _PointsShape = _pd_unhandled

    def Point(self, point: geo.Point, *args, **kwargs):
        try:
            return self._PointsShape(point, *args, **kwargs)
        except RuntimeError:
            pass
        try:
            return self._Rectangular(point, *args, **kwargs)
        except RuntimeError:
            pass
        return self._Shape(point)

    def Line(self, line: geo.Line, *args, **kwargs):
        try:
            return self._PointsShape(line, *args, **kwargs)
        except RuntimeError:
            pass
        try:
            return self._Rectangular(line, *args, **kwargs)
        except RuntimeError:
            pass
        return self._Shape(line)

    def Polygon(self, polygon: geo.Polygon, _dispatch_hier: bool=True, *args, **kwargs):
        try:
            return self._PointsShape(polygon, *args, **kwargs)
        except RuntimeError:
            pass
        if _dispatch_hier:
            return self._Shape(polygon)
        else:
            raise RuntimeError(
                "Internal error: unhandled dispatcher for object of type "
                f"{polygon.__class__.__name__}"
            )

    def Rect(self, rect: geo.Rect, *args, **kwargs):
        try:
            return self.Polygon(rect, _dispatch_hier=False, *args, **kwargs)
        except RuntimeError:
            pass
        try:
            return self._Rectangular(rect, *args, **kwargs)
        except RuntimeError:
            pass
        return self._Shape(rect, *args, **kwargs)

    def Ring(self, ring: geo.Ring, *args, **kwargs):
        try:
            return self.Polygon(ring, _dispatch_hier=False, *args, **kwargs)
        except RuntimeError:
            pass
        try:
            return self._Rectangular(ring, *args, **kwargs)
        except RuntimeError:
            pass
        return self._Shape(ring, *args, **kwargs)

    def MultiPartShape(self, mps: geo.MultiPartShape, *args, **kwargs):
        return self.Polygon(mps, *args, **kwargs)

    def MultiPartShape__Part(self, part: geo.MultiPartShape._Part, *args, **kwargs):
        return self(part._partshape, *args, **kwargs)

    def MultiShape(self, ms: geo.MultiShape, *args, **kwargs):
        return self._Shape(ms, *args, **kwargs)

    def RepeatedShape(self, rs: geo.RepeatedShape, *args, **kwargs):
        return self._Shape(rs, *args, **kwargs)

    def ArrayShape(self, array: geo.ArrayShape, *args, **kwargs):
        return self.RepeatedShape(array, *args, **kwargs)
