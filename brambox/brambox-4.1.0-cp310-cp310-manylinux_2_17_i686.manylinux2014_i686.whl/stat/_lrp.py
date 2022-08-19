#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Functions for generating LRP metrics
#   https://arxiv.org/pdf/1807.01696.pdf
#
import logging
import numpy as np
import pandas as pd
from ._matchboxes import match_box
from . import coordinates

__all__ = ['lrp']
log = logging.getLogger(__name__)


def lrp(det, anno, threshold=0.5, ignore=None):
    """ Computes the LRP_ metric between detection and annotation dataframe. |br|
    This function will return the different partial LRP values, as well as the total value.
    The points get computed for each confidence value in the detection dataset and are defined as follows:

    .. math::

        LRP_{IoU}   &= \\frac{1}{NUM_{TP}} \\sum_{i=1}^{NUM_{TP}} (1 - IoU(det_i, anno_{det\\_i}))

        LRP_{FP}    &= 1 - Precision    = \\frac{NUM_{FP}}{NUM_{det}}

        LRP_{FN}    &= 1 - Recall       = \\frac{NUM_{FN}}{NUM_{anno}}

        \\\\[5pt]

        LRP &= \\frac{1}{NUM_{FP} + NUM_{anno}} ( \\frac{NUM_{TP}}{1 - threshold} * LRP_{IoU} + NUM_{det} * LRP_{FP} + NUM_{anno} * LRP_{FN} )

            &= \\frac{1}{NUM_{FP} + NUM_{anno}} ( \\sum_{i=1}^{NUM_{TP}} \\frac{1 - IoU(det_i, anno_{det\\_i})}{1 - threshold} + NUM_{FP} + NUM_{FN} )

    Args:
        det (pandas.DataFrame): Dataframe with detections
        anno (pandas.DataFrame): Dataframe with annotations
        threshold (number): Threshold to count a detection as true positive (usually IoU); Default **0.5**
        ignore (boolean, optional): Whether to consider the ignore flag of annotations when matching detections; Default **True if ignored annotations found**

    Returns:
        pandas.Dataframe: DataFrame with 5 columns **('lrp', 'confidence', 'iou', 'fp', 'fn')** that contains the LRP points at different confidence thresholds

    Note:
        If ignore is true, this function will match the detections using :func:`~brambox.stat.coordinates.pdollar` and consider ignored annotations as regions
        that can be matched to multiple times,
        otherwise it will use a regular :func:`~brambox.stat.coordinates.iou` and discard the ignored labels.
        If there are no ignored annotations, this boils down to the same.

        By default (`ignore == None`), this function will check whether there are ignored annotations and set the ignore value accordingly.

    Note:
        If you want more control over the parameters to match detections (eg. Change the criteria to something else than IoU),
        you can call the :func:`brambox.stat.match_box` function and provide other arguments. |br|
        This function will first check whether the detection dataframe has tp/fp columns and the annotation dataframe has detection/criteria columns.
        If this is not the case, it will compute them.

    Warning:
        For some reason, this function does not return the exact same values as the `official github repository`_.
        As you can see for the Faster R-CNN (X101+FPN) example below,
        there is a small difference (mostly for :math:`LRP_{FP}`) between some of the elements:

        ========== ======= ========= ======== ========
        Framework  moLRP   moLRP_iou moLRP_fp moLRP_fn
        ========== ======= ========= ======== ========
        Brambox    0.662   0.171     0.249    0.415
        ---------- ------- --------- -------- --------
        cancam/LRP 0.663   0.171     0.256    0.413
        ========== ======= ========= ======== ========

        **Feel free to try and debug this**, as I (0phoff) do not seem to find where this difference comes from!

    .. _official github repository: https://github.com/cancam/LRP
    """
    # Compute TP/FP
    if not ({'tp', 'fp'}.issubset(det.columns) and {'detection', 'criteria'}.issubset(anno.columns)):
        if ignore is None:
            ignore = anno.ignore.any()
        crit = coordinates.pdollar if ignore else coordinates.iou
        label = len({*det.class_label.unique(), *anno.class_label.unique()}) > 1
        det, anno = match_box(det, anno, threshold, criteria=crit, class_label=label, ignore=2 if ignore else 0)
    else:
        log.info('Custom matching function was used. Make sure to enter same threshold as the matching function used, as this will otherwise result in wrong metrics.')
        if not det.confidence.is_monotonic_decreasing:
            det = det.sort_values('confidence', ascending=False)

    if ignore:
        num_annos = (~anno.ignore).sum()
        anno = anno[~anno.ignore]
    else:
        num_annos = len(anno.index)

    # Compute LRP
    matches = det.loc[(det.tp | det.fp), ['tp', 'fp', 'confidence']].astype('float')
    if len(matches.index) == 0:
        if num_annos == 0:
            log.warning('Cannot compute LRP without detections nor annotations')
            return pd.DataFrame({'lrp': [], 'confidence': [], 'iou': [], 'fp': [], 'fn': []})
        else:
            log.warning('Computing LRP statistic without detections. Setting single point (1,0)')
            return pd.DataFrame({'lrp': [1.0], 'confidence': [0.0], 'iou': [0.0], 'fp': [1.0], 'fn': [1.0]})

    matches['iou'] = 0
    matches.loc[anno.detection.dropna(), 'iou'] = (1 - anno.loc[anno.detection.notnull(), 'criteria'].values)
    matches = matches.reset_index(drop=True)

    summed = matches[['tp', 'fp', 'iou']].cumsum()
    lrp_fn = 1 - (summed.tp / num_annos)
    lrp_fp = 1 - (summed.tp / (summed.tp + summed.fp))
    lrp_iou = (summed.iou / summed.tp.replace({0: np.nan})).fillna(0)
    lrp_total = ((summed.tp / (1 - threshold)) * lrp_iou + (matches.index+1) * lrp_fp + num_annos * lrp_fn) / (summed.fp + num_annos)

    lrp = pd.DataFrame({'lrp': lrp_total, 'confidence': matches.confidence, 'iou': lrp_iou, 'fp': lrp_fp, 'fn': lrp_fn})
    lrp = lrp.loc[~lrp.confidence.duplicated(keep='last')].reset_index(drop=True)   # Only keep last point where detection confidence is the same
    return lrp
