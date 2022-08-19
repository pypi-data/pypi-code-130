#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Statistics on curves
#
import logging
import numpy as np
from scipy import integrate

__all__ = ['auc', 'auc_interpolated', 'peak', 'point', 'simplify', 'threshold']
log = logging.getLogger(__name__)


def auc(curve, x=None, y=None):
    """ Computes the area under the curve.

    Args:
        curve (pandas.DataFrame): dataframe containing the X- and Y-values of the curve
        x (string): Name of the column that holds the X-axis values; Default **None**
        y (string): Name of the column that holds the Y-axis values; Default **None**

    Returns:
        Number: Area under the curve

    Note:
        If you do not give this function an X and/or Y column,
        it will default to using ``columns[0]`` as Y and ``columns[1]`` as X. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.
    """
    if x is None:
        x = curve.columns[1]
    if y is None:
        y = curve.columns[0]

    if len(curve) == 0:
        return float('nan')

    if len(curve) == 1:
        curve = curve.loc[0]
        return curve[x] * curve[y]

    if not curve[x].is_monotonic_increasing:
        log.warning('Curve x-values are not sorted in increasing order. Sorting the values, but it might not give correct results if there are multiple points with the same x value!')
        curve = curve.sort_values(x)

    x = curve[x].values
    y = curve[y].values

    # Add first and last point
    x = np.insert(x, 0, 0)
    y = np.insert(y, 0, y[0])
    x = np.append(x, x[-1])
    y = np.append(y, 0)

    return integrate.trapz(y, x)


def auc_interpolated(curve, x=None, y=None, samples=101, range=(0, 1), side='right'):
    """ Computes the n-point interpolated area under the curve. |br|
    This function approximates the area under the curve,
    by computing the Y-values at evenly spaced points on the X-axis between ``[range[0], range[1]]``
    and then computing the average of these values.
    The cocoapi_ uses this method to compute the Average Precision of their smoothed PR-curves.

    While not completely equivalent, this method can be thought of as some kind of Riemann sum.
    A Riemann sum boils down to approximating a curve with rectangles (of equal width).
    The `side` argument defines which value to take for the height of each rectangle.
    Since our curves are made up of sparse points (as opposed to a continuous function),
    we cannot really compute a midpoint Riemann sum.

    .. figure:: /.static/docs/riemann.*
       :width: 100%
       :alt: Different Riemann sums

       Figure from `khan academy`_

    It is generally recommended to use a right Riemann sum for decreasing functions (eg. PR)
    and a left Riemann sum for increasing functions (eg. ROC),
    as this results in your approximated AUC value to be slightly underestimated,
    as opposed to being overestimated.

    Args:
        curve (pandas.DataFrame): dataframe containing the X- and Y-values of the curve
        x (string): Name of the column that holds the X-axis values; Default **None**
        y (string): Name of the column that holds the Y-axis values; Default **None**
        samples (number): Number of equally spaced samples to take on the X-axis; Default **101**
        range (2 numbers): Starting and stopping point for the AUC on the X-axis (inclusive); Default **[0,1]**
        side ('left' | 'right'): Whether to compute a left or right Riemann sum; Default **right**

    Returns:
        Number: Approximated area under the curve

    Note:
        If you do not give this function an X and/or Y column,
        it will default to using ``columns[0]`` as Y and ``columns[1]`` as X. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.

    Note:
        As stated above, this function is not exactly the same as computing a Riemann sum with equal width rectangles. |br|
        In this function, we interpolate the values with N points and compute the average of these points.
        A Riemann sum averages a curve with rectangles and N points would only generate N-1 rectangles. |br|
        This is expected behaviour, as the goal of this function is not to generate a perfect Riemann sum,
        but rather to get as close as the cocoapi as possible.

    .. _khan academy: https://www.khanacademy.org/math/ap-calculus-ab/ab-integration-new/ab-6-2/a/riemann-sums-review
    """
    side = side.lower()
    if x is None:
        x = curve.columns[1]
    if y is None:
        y = curve.columns[0]

    if len(curve) == 0:
        return float('nan')

    if not curve[x].is_monotonic_increasing:
        log.warning('Curve x-values are not sorted in increasing order. Sorting the values, but it might not give correct results if there are multiple points with the same x value!')
        curve = curve.sort_values(x)

    x = curve[x].values
    y = curve[y].values

    # Generate interpolated x array : start->end with samples steps (first is range[0], last is range[1])
    x_interpolated = np.linspace(*range[:2], samples)

    # Generate interpolated y array
    indices = np.searchsorted(x, x_interpolated, side=side)
    if side == 'left':
        # Left riemann sum, we want i-1 for each point, except exact matches (see np.searchsorted)
        indices[np.in1d(x_interpolated, x, invert=True)] -= 1
    else:
        # Right riemann sum, we want i-1 for exact matches (see np.searchsorted)
        indices[np.in1d(x_interpolated, x)] -= 1
    indices = indices[(indices < y.shape[0]) & (indices >= 0)]

    y_interpolated = y[indices]

    # Compute AUC as a Riemann sum
    return y_interpolated.sum() / samples


def peak(curve, maximum=True, y=None):
    """ Find the min/max Y-value on a curve.

    Args:
        curve (pandas.DataFrame): dataframe containing the X-, Y-values of the curve
        maximum (boolean, optional): Whether to search for the maximum or minimum value; Default **True**
        y (string): Name of the column that holds the Y-axis values; Default **None**

    Returns:
        curve row: Point of the curve that contains the peak

    Note:
        If you do not give this function an Y column,
        it will default to using ``columns[0]`` as Y. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.
    """
    if y is None:
        y = curve.columns[0]

    # Get correct position on curve
    if maximum:
        pt = curve[y].idxmax()
    else:
        pt = curve[y].idxmin()

    return curve.loc[pt]


def point(curve, threshold, x=None):
    """ Return the point on the curve that matches the given detection threshold.

    Args:
        curve (pandas.DataFrame): dataframe containing the X-, Y- and confidence values of the curve
        threshold (number): detection confidence threshold to match
        x (string): Name of the column that holds the X-axis values; Default **None**

    Returns:
        curve row: Point of the curve that matches the detection confidence threshold

    Note:
        If you do not give this function an X column,
        it will default to using ``columns[1]`` as X. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.

    Warning:
        If there are no detection confidence values higher than the given threshold, this function will return ``None``.
    """
    if x is None:
        x = curve.columns[1]

    # Sort curve by confidence
    if not curve['confidence'].is_monotonic_decreasing:
        curve = curve.sort_values('confidence', ascending=False)
    if not curve[x].is_monotonic_increasing:
        log.error('Curve x-values are not sorted in increasing order. This function works under the assumption that decreasing confidences, generate increasing X-values.')

    # Get last curve point where confidence >= threshold
    curve = curve[curve.confidence >= threshold]
    if curve.empty:
        return None
    return curve.loc[curve.index[-1]]


def simplify(curve, x=None, y=None):
    """ Simplify a curve dataframe by removing intermediate points on horizontal and vertical line segments.

    Brambox generates curves by computing a point for each detection in the dataframe.
    This makes it easy to refer a back from a point on the curve to the detections, which is really a nice feature in a lot of circumstances. |br|
    However, this does mean that a curve consists of a lot of different points, which might be redundant when plotting.
    When you don't care about referring back to the detections, you can use this function to reduce the number of points on your curve,
    which might be necessary in order to save space when saving the curve, or increase the performance when plotting it.

    Args:
        curve (pandas.DataFrame): dataframe containing the X- and Y-values of the curve
        x (string): Name of the column that holds the X-axis values; Default **None**
        y (string): Name of the column that holds the Y-axis values; Default **None**

    Returns:
        DataFrame: The same curve, but with all intermediate points on horizontal and vertical segments removed.

    Note:
        If you do not give this function an X and/or Y column,
        it will default to using ``columns[0]`` as Y and ``columns[1]`` as X. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.
    """
    if x is None:
        x = curve.columns[1]
    if y is None:
        y = curve.columns[0]

    if 'confidence' in curve.columns and not curve['confidence'].is_monotonic_decreasing:
        log.debug('Curve confidence values are not sorted in decreasing order. Sorting now...')
        curve = curve.sort_values('confidence', ascending=False)
    if not curve[x].is_monotonic_increasing:
        log.error('Curve x-values are not sorted in increasing order. This function works under the assumption that decreasing confidences, generate increasing X-values.')

    # Repeating X values
    xcol = curve[x]
    x_prev = xcol.shift(-1) == xcol
    x_next = xcol.shift(1) == xcol

    # Repeating Y values
    ycol = curve[y]
    y_prev = ycol.shift(-1) == ycol
    y_next = ycol.shift(1) == ycol

    # Filter
    x_filter = x_prev & x_next      # Filter data-points on horizontal line segments
    y_filter = y_prev & y_next      # Filter data-points on vertical line segments
    xy_filter = x_prev & y_prev     # Filter duplicate data-points
    return curve.loc[~(x_filter | y_filter | xy_filter)].copy()


def threshold(curve, column, value, first=True, x=None):
    """ Compute the necessary detection threshold value to reach a certain value on the curve.

    Args:
        curve (pandas.DataFrame): dataframe containing the X-, Y- and confidence values of the curve
        column (string): on which axis to reach the threshold
        value (number): threshold value to reach on the curve
        first (boolean, optional): whether to reach the first or last value bigger than the given value; Default **True**
        x (string): name of the column that holds the X-axis values; Default **None**

    Returns:
        curve row: Point of the curve at which the threshold is reached

    Note:
        If you do not give this function an X column,
        it will default to using ``columns[1]`` as X. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.

    Warning:
        If the value is not reached on the curve, this function will return ``None``.
    """
    if x is None:
        x = curve.columns[1]

    # Sort curve by x axis
    if not curve['confidence'].is_monotonic_decreasing:
        curve = curve.sort_values('confidence', ascending=False)
    if not curve[x].is_monotonic_increasing:
        log.error('Curve x-values are not sorted in increasing order. This function works under the assumption that decreasing confidences, generate increasing X-values.')

    # Get correct position on curve
    threshold = curve[column] >= value
    if not threshold.any():
        return None

    if first:
        loc = curve[threshold].index[0]
    else:
        loc = curve[threshold].index[-1]

    return curve.loc[loc]
