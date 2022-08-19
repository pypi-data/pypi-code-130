#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#
#   Functions for generating Miss rate vs FPPI curve values and calculating log average miss rate
#
import logging
import numpy as np
import pandas as pd
from scipy import interpolate
from ..util import np_col
from ._matchboxes import match_det
from . import coordinates

__all__ = ['mr_fppi', 'lamr']
log = logging.getLogger(__name__)


def mr_fppi(det, anno, threshold=0.5, ignore=None):
    """ Computes MR-FPPI-curve between detection and annotation dataframe.
    This function will match detections and annotations by computing the IoU.

    Args:
        det (pandas.DataFrame): Dataframe with detections
        anno (pandas.DataFrame): Dataframe with annotations
        threshold (number): Threshold to count a detection as true positive; Default **0.5**
        ignore (Boolean, optional): Whether to consider the ignore flag of annotations when matching detections; Default **True**

    Returns:
        pandas.Dataframe: DataFrame with 3 columns **('miss_rate', 'false_positives_per_image', 'confidence')**
        that has the points of the MR-FPPI-curve and matching detection confidence values.

    Note:
        If ignore is true, this function will match the detections using :func:`~brambox.stat.coordinates.pdollar` and consider ignored annotations as regions
        that can be matched to multiple times,
        otherwise it will use a regular :func:`~brambox.stat.coordinates.iou` and discard the ignored labels.
        If there are no ignored annotations, this boils down to the same.

        By default (`ignore == None`), this function will check whether there are ignored annotations and set the ignore value accordingly.

    Note:
        If you want more control over the parameters to match detections (eg. Change the criteria to something else than IoU),
        you can call the :func:`brambox.stat.match_det` function and provide other arguments. |br|
        This function will first check whether the detection dataframe has tp/fp columns and compute them otherwise.
    """
    if ignore is None:
        ignore = anno.ignore.any()

    # Compute TP/FP
    if not {'tp', 'fp'}.issubset(det.columns):
        crit = coordinates.pdollar if ignore else coordinates.iou
        label = len({*det.class_label.unique(), *anno.class_label.unique()}) > 1
        det = match_det(det, anno, threshold, criteria=crit, class_label=label, ignore=2 if ignore else 0)
    elif not det.confidence.is_monotonic_decreasing:
        det = det.sort_values('confidence', ascending=False)

    # Compute MR FPPI
    num_images = len(anno.image.cat.categories)
    if ignore:
        num_annos = (~anno.ignore).sum()
    else:
        num_annos = len(anno.index)

    matches = det.loc[(det.tp | det.fp), ['tp', 'fp', 'confidence']]
    if len(matches.index) == 0:
        if num_annos == 0:
            log.warning('Cannot compute MRFPPI without detections nor annotations')
            return pd.DataFrame({'miss_rate': [], 'false_positives_per_image': [], 'confidence': []})
        else:
            log.warning('Computing MRFPPI statistic without detections. Setting single point (1,0)')
            return pd.DataFrame({'miss_rate': [1.0], 'false_positives_per_image': [0.0], 'confidence': [0.0]})

    summed = matches[['tp', 'fp']].cumsum()
    mr = 1 - (summed.tp / num_annos).fillna(0)
    fppi = summed.fp / num_images

    mrfppi = pd.DataFrame({'miss_rate': mr, 'false_positives_per_image': fppi, 'confidence': matches.confidence})
    mrfppi = mrfppi.loc[~mrfppi.confidence.duplicated(keep='last')].reset_index(drop=True)      # Only keep last point where detection confidence is the same
    return mrfppi


def lamr(mr_fppi, samples=9):
    """ Computes log average miss-rate from a MR-FPPI-curve.

    The log average miss-rate is defined as the average of a number of evenly spaced log miss-rate samples
    on the :math:`{log}(FPPI)` axis within the range :math:`[10^{-2}, 10^{0}]`

    Args:
        mr_fppi (pandas.DataFrame): Miss-rate and FPPI values
        samples (int, optional): Number of samples within the given interval; Default **9**

    Returns:
        Number: log average miss-rate
    """
    if len(mr_fppi) <= 1:
        return float('nan')

    m = np_col(mr_fppi, 'miss_rate')
    f = np_col(mr_fppi, 'false_positives_per_image')

    s = np.logspace(-2., 0., samples)
    interpolated = interpolate.interp1d(f, m, fill_value=(1., 0.), bounds_error=False)(s)
    log_interpolated = np.log(interpolated)

    avg = sum(log_interpolated) / len(log_interpolated)
    return np.exp(avg)
