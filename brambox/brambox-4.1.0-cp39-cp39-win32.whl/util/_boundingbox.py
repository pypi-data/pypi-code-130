#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Bounding Box related functions
#
import logging
from enum import Enum
import numpy as np
import pandas as pd
from ._pd import np_col
from brambox._imports import pygeos, pgpd

__all__ = ['BoundingBoxTransformer', 'rasterize_segmentation', 'get_hbb', 'get_obb', 'get_poly', 'get_rasterized']
log = logging.getLogger(__name__)
RAD_45 = np.pi / 4
RAD_90 = np.pi / 2


def get_hbb(df, dilation=1, from_segmentation=None, as_segmentation=False, inplace=False):
    raise NotImplementedError('Use the brambox.util.BoundingBoxTransformer class instead')


def get_obb(df, dilation=1, as_segmentation=False, inplace=False):
    raise NotImplementedError('Use the brambox.util.BoundingBoxTransformer class instead')


def get_poly(df, inplace=False):
    raise NotImplementedError('Use the brambox.util.BoundingBoxTransformer class instead')


def get_rasterized(*args, **kwargs):
    log.error('This function has been renamed to rasterize_segmentation')
    return rasterize_segmentation(*args, **kwargs)


def rasterize_segmentation(df, out_shape, rescale=1, dtype=np.uint8, inplace=False, **kwargs):
    """ Get rasterized segmentation masks. |br|
    This function rasterizes the polygons from the 'segmentation' column into numpy arrays.

    By default the array will be full of zeros, with the polygon burned as ones.
    This can be modified by supplying the correct keyword arguments.

    Args:
        df (pandas.DataFrame): brambox dataframe with a segmentation column
        out_shape: output shape of the numpy arrays. This can be a list of different shapes for each of the polygons.
        rescale (number, optional): Rescaling factor for the shapes before burning them into the arrays; Default **1**
        dtype (numpy.dtype, optional): output data type for the numpy arrays. Check :func:`rasterio.features.rasterize` for valid types; Default **uint8**
        inplace (boolean, optional):
            Whether to return the computed columns are add them inplace in the existing dataframe; Default **False**
        kwargs: extra arguments that are passed to :func:`rasterio.features.rasterize`

    Returns:
        pandas.DataFrame or None:
        ``inplace=True``  None |br|
        ``inplace=False`` DataFrame where the "segmentation" column now contains rasterized numpy arrays

    Warning:
        This function requires rasterio and will raise an error if it is not installed!
    """
    from rasterio import features
    import affine

    # Get shape foreach element
    out_shape = np.asarray(out_shape)
    if out_shape.ndim == 1:
        out_shape = np.tile(out_shape, (len(df), 1))
    elif out_shape.shape[0] < len(df):
        raise ValueError('Not enough output shapes for the different polygons')

    # Setup transform
    if isinstance(rescale, (int, float)):
        rescale = (rescale,)
    tf = ~affine.Affine.scale(*rescale)
    kwargs['transform'] = kwargs.get('transform', affine.identity) * tf

    # TODO: Once PyGEOS implements the __geo_interface__, this is not necessary anymore
    polygons = df['segmentation'].array.to_shapely()
    lenpoly = polygons.shape[0]

    raster = pd.Series([
        features.rasterize(polygons[idx:idx+1], out_shape=out_shape[idx], dtype=dtype, **kwargs)
        for idx in range(lenpoly)
    ], index=df.index, dtype=object)

    if inplace:
        df['segmentation'] = raster
    else:
        df = df.copy()
        df['segmentation'] = raster
        return df


def hbb_bounds(poly, buffer):
    bounds = poly.geos.bounds()

    if buffer:
        # Buffer horizontally
        hor = bounds['xmin'] == bounds['xmax']
        bounds.loc[hor, 'xmin'] = bounds.loc[hor, 'xmin'] - buffer / 2
        bounds.loc[hor, 'xmax'] = bounds.loc[hor, 'xmax'] + buffer / 2

        # Buffer vertically
        ver = bounds['ymin'] == bounds['ymax']
        bounds.loc[ver, 'ymin'] = bounds.loc[ver, 'ymin'] - buffer / 2
        bounds.loc[ver, 'ymax'] = bounds.loc[ver, 'ymax'] + buffer / 2

    return bounds


def point_to_polygon(point):
    x = pygeos.get_x(point)
    y = pygeos.get_y(point)
    return pygeos.box(x, y, x, y)


def line_to_polygon(line):
    (x0, y0), (x1, y1) = pygeos.get_coordinates(line)
    return pygeos.normalize(pygeos.polygons([[x0, y0], [x1, y1], [x1, y1], [x0, y0], [x0, y0]]))


class BoundingBoxTransformer:
    """ Transform Bounding box dataframes between HBB, OBB and Instance Segmentation.

    Args:
        df (pandas.DataFrame): Bounding box dataframe you wish to transform

    Examples:
        >>> # Load HBB data
        >>> df_hbb = bb.io.load(...)
        >>> # Get data as OBB (will have all angles at zero, because input is HBB)
        >>> df_obb = BoundingBoxTransformer(df_hbb).get_obb()
        >>> # Get HBB as polygons
        >>> df_poly = BoundingBoxTransformer(df_hbb).get_poly()
        >>> # Get HBB polygons (will be the same as above, because input is HBB)
        >>> df_poly_hbb = BoundingBoxTransformer(df_hbb).get_hbb_poly()

        >>> # Load segmentation data
        >>> df_poly = bb.io.load(...)
        >>> # Get data as OBB
        >>> df_obb = BoundingBoxTransformer(df_poly).get_obb()
        >>> # Get OBB polygons (x,y,w,h columns will be the HBB bounds of the OBB polygons)
        >>> df_poly_obb = BoundingBoxTransformer(df_poly).get_obb_poly()

    Note:
        The input dataframe should be one of the following types:

        HBB
            Contains `x_top_left`, `y_top_left`, `width`, `height` positional columns
        OBB
            Contains `x_top_left`, `y_top_left`, `width`, `height`, `angle` positional columns
        Poly
            Contains `x_top_left`, `y_top_left`, `width`, `height`, `segmentation` positional columns

        When using dataframes with a `segmentation` column (Poly type), they can have **None** as valid segmentation geometry.
        In those cases, we compute a new geometry polygon (horizontal box) based on the HBB data columns.
    """
    class Type(Enum):
        EMPTY = 0
        HBB = 1
        OBB = 2
        SEG = 3

    def __init__(self, df):
        self.df = df

        # Get most accurate polygon
        if len(self.df) == 0:
            self.__type = self.Type.EMPTY
            self.poly = None
        elif 'segmentation' in self.df.columns:
            self.__type = self.Type.SEG
            self.poly = self.df['segmentation'].copy()
            null = pd.isna(self.poly)
            if null.any():
                self.poly.loc[null] = pygeos.box(
                    df.loc[null, 'x_top_left'].values,
                    df.loc[null, 'y_top_left'].values,
                    df.loc[null, 'x_top_left'].values + df.loc[null, 'width'].values,
                    df.loc[null, 'y_top_left'].values + df.loc[null, 'height'].values,
                )
        elif 'angle' in self.df.columns:
            self.__type = self.Type.OBB
            w, h, a = df['width'].to_numpy(), df['height'].to_numpy(), df['angle'].to_numpy()
            side1 = np.stack((w * np.cos(a), -w * np.sin(a)), -1)
            side2 = np.stack((h * np.sin(a), h * np.cos(a)), -1)

            tl = df[['x_top_left', 'y_top_left']].to_numpy()
            tr = tl + side1
            br = tr + side2
            bl = br - side1
            points = np.array((tl, tr, br, bl)).swapaxes(0, 1)

            self.poly = pd.Series(pygeos.polygons(points), index=df.index, dtype='geos')
        else:
            self.__type = self.Type.HBB
            self.poly = pd.Series(
                pygeos.box(
                    np_col(df, 'x_top_left'),
                    np_col(df, 'y_top_left'),
                    np_col(df, 'x_top_left') + np_col(df, 'width'),
                    np_col(df, 'y_top_left') + np_col(df, 'height'),
                ),
                index=df.index,
                dtype='geos',
            )

    def get_hbb(self, buffer=0):
        """ Transform the dataframe to an HBB version. |br|
        This method will return a dataframe with the
        ``[x_top_left, y_top_left, width, height]`` localization columns.

        Args:
            buffer (int, optional): widht/height buffer for the bounding boxes; Default **1**

        Note:
            When `buffer` is greater than zero, we buffer bounding boxes that have a width/height of zero,
            by adding ``buffer / 2`` values to each side of the box.
        """
        if self.__type == self.Type.EMPTY:
            return self.df.drop(columns=['angle', 'segmentation'], errors='ignore')

        if self.__type == self.Type.HBB:
            return self.df.copy()

        # Get buffered bounds
        bounds = hbb_bounds(self.poly, buffer)

        # Get return dataframe
        df = self.df.drop(columns=['angle', 'segmentation'], errors='ignore')
        df['x_top_left'] = bounds['xmin']
        df['y_top_left'] = bounds['ymin']
        df['width'] = bounds['xmax'] - bounds['xmin']
        df['height'] = bounds['ymax'] - bounds['ymin']

        return df

    def get_obb(self, buffer=0):
        """ Transform the dataframe to an OBB version. |br|
        This method will return a dataframe with the
        ``[x_top_left, y_top_left, width, height, angle]`` localization columns.

        The angle is in radians and will be between -45° and 45°.
        A negative angle means that the box should be rotated clock-wise and a positive angle counter-clock-wise.

        Args:
            buffer (int, optional): widht/height buffer for the bounding boxes; Default **1**

        Warning:
            While this bounding box format is necessary in some situations,
            keep in mind that this is not an "official" brambox format and that most functions will not work correctly.
            The official brambox format simply consists of `x_top_left`, `y_top_left`, `width` and `height` horizontal bounds data,
            with an optional `segmentation` mask data.

            The :meth:`~brambox.util.BoundingBoxTransformer.get_obb_poly` method returns the correct OBB dataframe.

        Note:
            When `buffer` is greater than zero, we buffer bounding boxes that have a width/height of zero,
            by adding ``buffer / 2`` values to each side of the box.
        """
        if self.__type == self.Type.EMPTY:
            df = self.df.drop(columns=['angle', 'segmentation'], errors='ignore')
            df['angle'] = []
            return df

        if self.__type == self.Type.OBB:
            return self.df.copy()

        # Get obb coordinates
        obb = self.poly.geos.oriented_envelope()
        types = obb.geos.get_type_id()
        if buffer:
            obb.loc[types == 0] = obb.loc[types == 0].geos.buffer(buffer/2, quadsegs=1, cap_style='square', join_style='bevel')
            obb.loc[types == 1] = obb.loc[types == 1].geos.buffer(buffer/2, quadsegs=1, cap_style='flat', join_style='bevel')
        else:
            obb.loc[types == 0] = obb.loc[types == 0].apply(point_to_polygon)
            obb.loc[types == 1] = obb.loc[types == 1].apply(line_to_polygon)

        coords = pygeos.get_coordinates(obb.values, include_z=False).reshape(obb.shape[0], 5, 2)

        # Compute width and height
        dx = coords[:, 1, 0] - coords[:, 0, 0]
        dy = coords[:, 1, 1] - coords[:, 0, 1]
        s1 = (dx ** 2 + dy ** 2) ** 0.5
        s2 = ((coords[:, 2, 0] - coords[:, 1, 0]) ** 2 + (coords[:, 2, 1] - coords[:, 1, 1]) ** 2) ** 0.5

        # Compute angle
        with np.errstate(divide='ignore'):
            angle = np.arctan(dy / dx)
        angle[dx == 0] = RAD_90
        cw = angle >= 0
        angle = np.abs(angle)

        # Select correct width, height and angle
        #   - abs(angle) should be between 0,45
        #       -> otherwise take 90-abs(angle)
        #       -> flip h,w,cw
        #   - We have a flipped Y-axis
        #       -> inverse angle sign (make CW negative, as we took abs)
        w = s1.copy()
        h = s2.copy()
        change = angle > RAD_45
        w[change] = s2[change]
        h[change] = s1[change]
        angle[change] = RAD_90 - angle[change]
        cw[change] = ~cw[change]
        angle[cw] = -angle[cw]

        # Compute X and Y (top left)
        #   - CW -> Smallest X as corner
        #   - CCW -> Smallest Y as corner
        idx = np.argmin(coords, 1)
        tl = np.take_along_axis(coords, np.expand_dims(idx[:, 0:1], axis=1), axis=1).squeeze(axis=1)
        y = np.take_along_axis(coords, np.expand_dims(idx[:, 1:2], axis=1), axis=1).squeeze(axis=1)
        tl[cw] = y[cw]

        # Get return dataframe
        df = self.df.drop(columns='segmentation', errors='ignore')
        df['x_top_left'] = tl[:, 0]
        df['y_top_left'] = tl[:, 1]
        df['width'] = w
        df['height'] = h
        df['angle'] = angle

        return df

    def get_poly(self, buffer=0, buffer_poly=0, force_poly=False):
        """ Transform the dataframe to an Instance Segmentation version. |br|
        This method gets the most accuract segmentation geometries it can and then computes HBB boundaries from those.
        It will thus return a dataframe with the
        ``[x_top_left, y_top_left, width, height, segmentation]`` localization columns.

        Args:
            buffer (int, optional): widht/height buffer for the bounding boxes; Default **1**
            buffer_poly (int, optional): width/height buffer value for the segmentation polgons; Default **0**
            force_poly (bool, optional): Whether to transform Lines/Points to Polygons (only if `buffer_poly` is 0); Default **False**

        Note:
            This method has 2 different buffering arguments:

            buffer_poly
                Buffering for the geometries.
                If you set this to a value higher than 0, we buffer line and point geometries to polygons, by adding ``buffer_poly / 2`` to each side.
                The default value of zero has as effect that your segmentation can contain lines and points (unless you `force_poly`).

            buffer
                Buffering value for the x, y, w, h bounds.
                See :meth:`~brambox.util.BoundingBoxTransformer.get_hbb` for more information.

            If you set `buffer_poly`, all Line/Point geometries will already have been buffered to polygons
            and `buffer` will thus have no effect.
        """
        if self.__type == self.Type.EMPTY:
            df = self.df.drop(columns=['angle', 'segmentation'], errors='ignore')
            df['segmentation'] = pgpd.GeosArray([])
            return df

        poly = self.poly.copy()
        types = poly.geos.get_type_id()
        if buffer_poly:
            poly.loc[types == 0] = poly.loc[types == 0].geos.buffer(buffer_poly/2, quadsegs=1, cap_style='square', join_style='bevel')
            poly.loc[types == 1] = poly.loc[types == 1].geos.buffer(buffer_poly/2, quadsegs=1, cap_style='flat', join_style='bevel')
        elif force_poly:
            poly.loc[types == 0] = poly.loc[types == 0].apply(point_to_polygon)
            poly.loc[types == 1] = poly.loc[types == 1].apply(line_to_polygon)

        # Get buffered bounds
        bounds = hbb_bounds(poly, buffer)

        # Get return dataframe
        df = self.df.drop(columns='angle', errors='ignore')
        df['segmentation'] = poly
        df['x_top_left'] = bounds['xmin']
        df['y_top_left'] = bounds['ymin']
        df['width'] = bounds['xmax'] - bounds['xmin']
        df['height'] = bounds['ymax'] - bounds['ymin']

        return df

    def get_hbb_poly(self, buffer=0, buffer_poly=0, force_poly=False):
        """ Transform the dataframe to an Instance Segmentation version,
        where the geometries are all HBB's. |br|
        This methods will return a dataframe with the
        ``[x_top_left, y_top_left, width, height, segmentation]`` localization columns.

        Args:
            buffer (int, optional): widht/height buffer for the bounding boxes; Default **1**
            buffer_poly (int, optional): width/height buffer value for the segmentation polgons; Default **0**
            force_poly (bool, optional): Whether to transform Lines/Points to Polygons (only if `buffer_poly` is 0); Default **False**

        Note:
            This method has 2 different buffering arguments:

            buffer_poly
                Buffering for the geometries.
                If you set this to a value higher than 0, we buffer line and point geometries to polygons, by adding ``buffer_poly / 2`` to each side.
                The default value of zero has as effect that your segmentation can contain lines and points (unless you `force_poly`).

            buffer
                Buffering value for the x, y, w, h bounds.
                See :meth:`~brambox.util.BoundingBoxTransformer.get_hbb` for more information.

            If you set `buffer_poly`, all Line/Point geometries will already have been buffered to polygons
            and `buffer` will thus have no effect.
        """
        if self.__type == self.Type.EMPTY:
            df = self.df.drop(columns=['angle', 'segmentation'], errors='ignore')
            df['segmentation'] = pgpd.GeosArray([])
            return df

        # Get HBB poly
        hbb = self.poly.geos.envelope()

        # Envelope creates polygons from linestrings, so revert (only affects horizontal / vertical lines)
        poly_types = self.poly.geos.get_type_id()
        hbb.loc[poly_types == 1] = hbb.loc[poly_types == 1].geos.make_valid()

        types = hbb.geos.get_type_id()
        if buffer_poly:
            hbb.loc[types == 0] = hbb.loc[types == 0].geos.buffer(buffer_poly/2, quadsegs=1, cap_style='square', join_style='bevel')
            hbb.loc[types == 1] = hbb.loc[types == 1].geos.buffer(buffer_poly/2, quadsegs=1, cap_style='flat', join_style='bevel')
        elif force_poly:
            hbb.loc[types == 0] = hbb.loc[types == 0].apply(point_to_polygon)
            hbb.loc[types == 1] = hbb.loc[types == 1].apply(line_to_polygon)

        # Get buffered bounds
        bounds = hbb_bounds(hbb, buffer)

        # Get return dataframe
        df = self.df.drop(columns='angle', errors='ignore')
        df['segmentation'] = hbb
        df['x_top_left'] = bounds['xmin']
        df['y_top_left'] = bounds['ymin']
        df['width'] = bounds['xmax'] - bounds['xmin']
        df['height'] = bounds['ymax'] - bounds['ymin']

        return df

    def get_obb_poly(self, buffer=0, buffer_poly=0, force_poly=False):
        """ Transform the dataframe to an Instance Segmentation version,
        where the geometries are all OBB's. |br|
        This method computes the OBB geometry from the most accuract segmentation geometries and then computes HBB boundaries from those.
        It will thus return a dataframe with the
        ``[x_top_left, y_top_left, width, height, segmentation]`` localization columns.

        Args:
            buffer (int, optional): widht/height buffer for the bounding boxes; Default **1**
            buffer_poly (int, optional): width/height buffer value for the segmentation polgons; Default **0**
            force_poly (bool, optional): Whether to transform Lines/Points to Polygons (only if `buffer_poly` is 0); Default **False**

        Note:
            This method has 2 different buffering arguments:

            buffer_poly
                Buffering for the geometries.
                If you set this to a value higher than 0, we buffer line and point geometries to polygons, by adding ``buffer_poly / 2`` to each side.
                The default value of zero has as effect that your segmentation can contain lines and points (unless you `force_poly`).

            buffer
                Buffering value for the x, y, w, h bounds.
                See :meth:`~brambox.util.BoundingBoxTransformer.get_hbb` for more information.

            If you set `buffer_poly`, all Line/Point geometries will already have been buffered to polygons
            and `buffer` will thus have no effect.
        """
        if self.__type == self.Type.EMPTY:
            df = self.df.drop(columns=['angle', 'segmentation'], errors='ignore')
            df['segmentation'] = pgpd.GeosArray([])
            return df

        # Get OBB poly
        obb = self.poly.geos.oriented_envelope()
        types = obb.geos.get_type_id()
        if buffer_poly:
            obb.loc[types == 0] = obb.loc[types == 0].geos.buffer(buffer_poly/2, quadsegs=1, cap_style='square', join_style='bevel')
            obb.loc[types == 1] = obb.loc[types == 1].geos.buffer(buffer_poly/2, quadsegs=1, cap_style='flat', join_style='bevel')
        elif force_poly:
            obb.loc[types == 0] = obb.loc[types == 0].apply(point_to_polygon)
            obb.loc[types == 1] = obb.loc[types == 1].apply(line_to_polygon)

        # Get buffered bounds
        bounds = hbb_bounds(obb, buffer)

        # Get return dataframe
        df = self.df.drop(columns='angle', errors='ignore')
        df['segmentation'] = obb
        df['x_top_left'] = bounds['xmin']
        df['y_top_left'] = bounds['ymin']
        df['width'] = bounds['xmax'] - bounds['xmin']
        df['height'] = bounds['ymax'] - bounds['ymin']

        return df
