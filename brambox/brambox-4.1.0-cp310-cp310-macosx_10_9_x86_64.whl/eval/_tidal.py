#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Functions for computing tide statistics
#   https://github.com/dbolya/tide
#
import logging
import numpy as np
import pandas as pd
from collections import defaultdict
from tqdm.auto import tqdm as _tqdm
from .. import stat
from .. import util
from ..util._logaggregator import LogAggregator
from ._cache import Cache

__all__ = ['TIDAL']
log = logging.getLogger(__name__)


class TIDAL:
    """
    Toolbox for Identifying Detection Accuracy Losses. |br|
    This tool is an adaptation of :class:`~brambox.eval.TIDE`, with a few differences:

    - More specific categories (CLS, DUP, LOC, CLS+DUP, CLS+LOC, DUP+LOC, CLS+DUP+LOC, BKG, MISS)
    - TIDE matches errors in the following order: localization > classification > duplicate > background > both (=CLS+LOC).
      This means that if the detection has an IoU between the background and positive threshold for a localization error,
      it will be marked as such, regardless of whether there is a better IoU for a classification error. |br|
      TIDAL works slightly differently. We first get the best IoU between an erroneous detection and all unmatched (missing) annotations.
      If the IoU is higher than the background threshold, we use that detection-annotation pair to figure out which error it is (CLS,LOC,CLS+LOC).
      If not, we take the highest IoU between the detection and all annotations (regardless whether they have a matching TP detection)
      and use that pair to figure out the error (DUP,CLS+DUP,DUP+LOC,CLS+DUP+LOC,BKG).
    - By default TIDAL rescales the mdAP values, so that the mAP+errors and mAP+fpfn is equal to 100%.
      TIDE inherently does something similar, by plotting the errors in a pie chart, but does not take the actual mAP into account.
      You can disable this behaviour by setting ``rescale_mdap`` to **False**.

    Args:
        detection (pd.DataFrame): brambox detection dataframe
        annotation (pd.DataFrame): brambox annotation dataframe
        pos_thresh (float, optional): IoU threshold to count a detection as a true positive; Default **0.5**
        bg_thresh (float, optional): IoU threshold to count a detection as a background error (as opposed to a localisation error); Default **0.1**
        max_det (int, optional): Maximum number of detections per image (set to **None** to disable); Default **100**
        area_range(tuple of 2 numbers, optional): Area range to filter bounding boxes (See Note below); Default **None**
        simplified (bool, optional): Whether to aggregate error categories to have the same as TIDE (CLS+DUP, DUP+LOC and CLS+DUP+LOC into BKG); Default **False**
        rescale_mdap (bool, optional): Whether to rescale the mdAP values, so the sum of mAP and mdAP is equal to 1 (fp/fn separate from other categories); Default **True**
        tqdm (bool, optional): Whether to show a progress bar with tqdm; Default **True**

    Note:
        Duplicate errors can only occur if an annotation already matches with a True Positive detection (aka this object has already been found).

        If 2 erroneous detections are paired with the same (unmatched/missing) annotation, you might expect the 2nd detection to be labeled as a duplicate error.
        However, this is not the case as both erroneous detections are simply a localisation/classification error, when regarded individually.

        The reasoning behind this is that if you fix the error for these 2 detections (eg. get a model with a better localization),
        you might not have that duplicate problem anymore, as systems like NMS will have filtered the 2nd bounding box.
        If your model still outputs 2 better localized boxes, then one of them will be labeled as a true positive and the other as a duplicate error.
        You have thus created a new model, which does not have the same characteristics and errors.
    """
    coco_areas = {
        'small':    [None, 32**2],
        'medium':   [32**2, 96**2],
        'large':    [96**2, None],
    }                                                       #: Different coco area ranges which you can use with TIDAL

    def __init__(
        self,
        detection,
        annotation,
        pos_thresh=0.5,
        bg_thresh=0.1,
        max_det=100,
        area_range=None,
        simplified=False,
        rescale_mdap=True,
        tqdm=True,
    ):
        self.pos_thresh = pos_thresh
        self.bg_thresh = bg_thresh
        self.area_range = area_range if area_range is not None else (None, None)
        self.simplified = simplified
        self.rescale_mdap = rescale_mdap
        self.tqdm = tqdm

        # Get dataframes
        self.annotation = annotation.copy()
        if max_det is not None:
            self.detection = (
                detection
                .sort_values('confidence', ascending=False)
                .groupby('image', sort=False)
                .head(max_det)
                .reset_index(drop=True)
            )
        else:
            self.detection = detection.copy()

        if area_range is not None:
            self.annotation['area'] = self.annotation.width * self.annotation.height
            self.detection['area'] = self.detection.width * self.detection.height

        # Get class labels
        anno_label = set(self.annotation.class_label.unique())
        det_label = set(self.detection.class_label.unique())
        self.class_label = anno_label | det_label
        if anno_label != det_label:
            log.error('Annotations and Detections do not contain the same class labels! Computing all labels.')

        # Check images
        if set(self.annotation.image.cat.categories) != set(self.detection.image.cat.categories):
            log.error('Annotation and Detection dataframe do not contain the same image categories! Computing for all images.')

        # Initialize private fields
        self.cache = Cache(
            'error_detections',
            'error_annotations',
            'AP',
            'dAP_classification',
            'dAP_duplicate',
            'dAP_localisation',
            'dAP_classification_duplicate',
            'dAP_classification_localisation',
            'dAP_duplicate_localisation',
            'dAP_classification_duplicate_localisation',
            'dAP_background',
            'dAP_missed',
            'dAP_fn',
            'dAP_fp',
        )

    def reset(self):
        """ Resets the cache. """
        self.cache.reset()

    def compute(self, *values):
        """
        Compute the different mdAP values.

        Args:
            values (string): Which values to recompute (names from cache)

        Warning:
            This function performs the actual computation, but returns nothing.
            You should probably never call this function, but instead access the various properties of this class,
            as they automatically call compute with the right values.
        """
        # Check if recompute is necessary
        recompute = defaultdict(bool, {val: val not in self.cache for val in values})
        if not any(recompute.values()):
            return

        # Setup dictionaries
        for name in recompute.keys():
            self.cache[name] = {}

        # Match detections and annotations
        dm, am = self.compute_matches(self.detection, self.annotation, self.pos_thresh)
        dm = dm.reset_index(drop=True)
        am = am.reset_index(drop=True)

        # Find Error Types
        err_det = util.DualGroupBy(dm, am, 'image', group_keys=False).apply(find_errors, pos_thresh=self.pos_thresh, bg_thresh=self.bg_thresh).set_index('index')
        if recompute['error_detections']:
            tmp = err_det.drop(['anno'], axis=1).fillna(value=True).astype('int')
            tmp['none'] = 0.1
            tmp = tmp.idxmax(axis=1)
            tmp[tmp == 'none'] = pd.NA
            error_detections = dm.drop(['tp', 'fp'], axis=1)
            error_detections['error'] = tmp
            self.cache['error_detections'] = error_detections
            recompute['error_detections'] = False

        err_det['anno_label'] = dm.class_label
        err_det.loc[err_det.anno.notnull(), 'anno_label'] = am.class_label[err_det.anno[err_det.anno.notnull()]].values

        fn_anno = list(set(am.detection[am.detection.isnull()].index) - set(err_det.anno[err_det.anno.notnull()].unique()))
        fn_anno = np.array(fn_anno, dtype='int')

        if recompute['error_annotations']:
            tmp = np.zeros(len(self.annotation.index), dtype='bool')
            tmp[fn_anno] = True
            error_annotations = am.drop(['detection', 'criteria'], axis=1)
            error_annotations['error'] = tmp
            error_annotations['error'] = error_annotations['error'].map({True: 'missed', False: pd.NA})
            self.cache['error_annotations'] = error_annotations
            recompute['error_annotations'] = False

        am_nofn = np.ones(len(am.index), dtype='bool')
        am_nofn[fn_anno] = False
        am_nofn = am[am_nofn]

        # No recomputes
        if not any(recompute.values()):
            return

        # Compute AP
        if 'AP' not in self.cache:
            self.cache['AP'] = {}
            recompute['AP'] = True

        # Fix Errors
        def fix_errors(error_type, mask, set_tp=True):
            if isinstance(error_type, str):
                err = err_det.loc[mask, error_type].copy()
            else:
                err = err_det.loc[mask, error_type].any(axis=1)

            err_null = err.isnull()
            err[err_null] = False

            dc_err = dm.loc[mask].copy()
            dc_err.loc[(err | err_null), 'fp'] = False
            if set_tp:
                dc_err.loc[err, 'tp'] = True

            return self.compute_ap(dc_err, ac, self.pos_thresh)

        cl_iter = _tqdm(self.class_label, desc='Fixing Errors') if self.tqdm else self.class_label
        for label in cl_iter:
            if self.tqdm:
                cl_iter.set_postfix(label=label)

            det_label_mask = dm.class_label == label
            cls_label_mask = err_det.anno_label == label

            with LogAggregator(msg=f'[{label}] {{}}'):
                # Regular AP
                if recompute['AP']:
                    dc = dm.loc[det_label_mask]
                    ac = am.loc[am.class_label == label]
                    self.cache['AP'][label] = self.compute_ap(dc, ac, self.pos_thresh)

                if recompute['dAP_classification']:
                    self.cache['dAP_classification'][label] = fix_errors(
                        'classification',
                        cls_label_mask,
                    )
                if recompute['dAP_duplicate']:
                    self.cache['dAP_duplicate'][label] = fix_errors(
                        'duplicate',
                        det_label_mask,
                        set_tp=False,
                    )
                if recompute['dAP_localisation']:
                    self.cache['dAP_localisation'][label] = fix_errors(
                        'localisation',
                        det_label_mask,
                    )
                if recompute['dAP_classification_duplicate']:
                    self.cache['dAP_classification_duplicate'][label] = fix_errors(
                        'classification_duplicate',
                        cls_label_mask,
                        set_tp=False,
                    )
                if recompute['dAP_classification_localisation']:
                    self.cache['dAP_classification_localisation'][label] = fix_errors(
                        'classification_localisation',
                        cls_label_mask,
                    )
                if recompute['dAP_duplicate_localisation']:
                    self.cache['dAP_duplicate_localisation'][label] = fix_errors(
                        'duplicate_localisation',
                        det_label_mask,
                        set_tp=False,
                    )
                if recompute['dAP_classification_duplicate_localisation']:
                    self.cache['dAP_classification_duplicate_localisation'][label] = fix_errors(
                        'classification_duplicate_localisation',
                        cls_label_mask,
                        set_tp=False,
                    )
                if recompute['dAP_background']:
                    categories = 'background' if not self.simplified else ['background', 'classification_duplicate', 'duplicate_localisation', 'classification_duplicate_localisation']
                    self.cache['dAP_background'][label] = fix_errors(
                        categories,
                        det_label_mask,
                        set_tp=False,
                    )
                if recompute['dAP_missed']:
                    ac_err = am_nofn[am_nofn.class_label == label]
                    self.cache['dAP_missed'][label] = self.compute_ap(
                        dc,
                        ac_err,
                        self.pos_thresh,
                    )
                if recompute['dAP_fp']:
                    dc_fp = dc.copy()
                    dc_fp['fp'] = False
                    self.cache['dAP_fp'][label] = self.compute_ap(
                        dc_fp,
                        ac,
                        self.pos_thresh,
                    )
                if recompute['dAP_fn']:
                    ac_fn = ac.copy()
                    ac_fn = ac_fn[~(ac_fn.detection.isnull())]
                    self.cache['dAP_fn'][label] = self.compute_ap(
                        dc,
                        ac_fn,
                        self.pos_thresh,
                    )

        # Create dataframes
        if isinstance(self.cache['AP'], dict):
            self.cache['AP'] = pd.Series(self.cache['AP'])

        for name, value in recompute.items():
            if value and name != 'AP':
                self.cache[name] = pd.Series(self.cache[name]) - self.cache['AP']

    def compute_matches(self, det, anno, iou):
        """ This function performs the actual matching of detections and annotations.
        It returns TP/FP columns for the detections and detection/criteria for the annotations. |br|
        This has been implemented as a separate function, so that you can inherit from this class and only overwrite this method and provide your own.

        Args:
            det (pd.DataFrame): brambox detection dataframe of only one class
            anno (pd.DataFrame): brambox detection dataframe of only one class
            iou (float): Intersection over Union values between 0 and 1
        """
        # Prepare annotations
        # Existing ignore annotations are considered regions and thus are matched with IgnoreMethod.MULTIPLE
        # We set annotations whose areas dont fall within the range to ignore, but they should be matched with IgnoreMethod.SINGLE
        # This also means the pdollar criteria will compute IoA for existing ignore regions, but IoU for detections outside of range
        anno = anno.copy()
        anno['ignore_method'] = stat.IgnoreMethod.SINGLE
        anno.loc[anno.ignore, 'ignore_method'] = stat.IgnoreMethod.MULTIPLE
        if self.area_range[0] is not None:
            anno.loc[anno.area < self.area_range[0], 'ignore'] = True
        if self.area_range[1] is not None:
            anno.loc[anno.area > self.area_range[1], 'ignore'] = True

        # Match annotations and detections
        # Afterwards, we filter the remaining detection boxes which are outside of the range and were not matched
        dm, am = stat.match_box(det, anno, iou, class_label=True, ignore=stat.IgnoreMethod.INDIVIDUAL)
        if self.area_range[0] is not None:
            dm.loc[dm.area < self.area_range[0], 'fp'] = False
        if self.area_range[1] is not None:
            dm.loc[dm.area > self.area_range[1], 'fp'] = False

        return dm, am

    def compute_ap(self, det, anno, iou):
        """ This function does the actual AP computation for annotations and detections of a specific class_label. |br|
        This has been implemented as a separate function, so that you can inherit from this class and only overwrite this method and provide your own.

        Args:
            det (pd.DataFrame): brambox detection dataframe of only one class, which has already been matched
            anno (pd.DataFrame): brambox detection dataframe of only one class, which has already been matched
            iou (float): Intersection over Union values between 0 and 1
        """
        return stat.auc_interpolated(stat.pr(det, anno, iou, smooth=True))

    @property
    def mdAP(self):
        """ Compute and return all mdAP values, as wel as the mAP. """
        if self.simplified:
            err_categories = [
                'dAP_classification',
                'dAP_duplicate',
                'dAP_localisation',
                'dAP_classification_localisation',
                'dAP_background',
                'dAP_missed',
            ]
        else:
            err_categories = [
                'dAP_classification',
                'dAP_duplicate',
                'dAP_localisation',
                'dAP_classification_duplicate',
                'dAP_classification_localisation',
                'dAP_duplicate_localisation',
                'dAP_classification_duplicate_localisation',
                'dAP_background',
                'dAP_missed',
            ]

        categories = ['AP', 'dAP_fp', 'dAP_fn', *err_categories]
        self.compute(*categories)
        mdap = pd.Series({f'm{cat}': self.cache[cat].mean(skipna=True) for cat in categories})

        if self.rescale_mdap:
            mAP_left = 1 - mdap['mAP']

            err_sum = mdap[[f'm{cat}' for cat in err_categories]].sum()
            err_factor = mAP_left / err_sum
            for cat in err_categories:
                mdap[f'm{cat}'] *= err_factor

            fpfn_sum = mdap['mdAP_fp'] + mdap['mdAP_fn']
            fpfn_factor = mAP_left / fpfn_sum
            mdap['mdAP_fp'] *= fpfn_factor
            mdap['mdAP_fn'] *= fpfn_factor

        return mdap

    @property
    def AP(self):
        """ Per class average precision """
        self.compute('AP')
        return self.cache['AP'].copy()

    @property
    def dAP_classification(self):
        """ Per class delta AP for classification errors. """
        self.compute('dAP_classification')
        return self.cache['dAP_classification'].copy()

    @property
    def dAP_duplicate(self):
        """ Per class delta AP for duplicate errors. """
        self.compute('dAP_duplicate')
        return self.cache['dAP_duplicate'].copy()

    @property
    def dAP_localisation(self):
        """ Per class delta AP for localisation errors. """
        self.compute('dAP_localisation')
        return self.cache['dAP_localisation'].copy()

    @property
    def dAP_classification_duplicate(self):
        """ Per class delta AP for classification_duplicate errors. """
        if self.simplified:
            raise NotImplementedError('This category does not exist in simplified mode')
        self.compute('dAP_classification_duplicate')
        return self.cache['dAP_classification_duplicate'].copy()

    @property
    def dAP_classification_localisation(self):
        """ Per class delta AP for classification_localisation errors. """
        self.compute('dAP_classification_localisation')
        return self.cache['dAP_classification_localisation'].copy()

    @property
    def dAP_duplicate_localisation(self):
        """ Per class delta AP for duplicate_localisation errors. """
        if self.simplified:
            raise NotImplementedError('This category does not exist in simplified mode')
        self.compute('dAP_duplicate_localisation')
        return self.cache['dAP_duplicate_localisation'].copy()

    @property
    def dAP_classification_duplicate_localisation(self):
        """ Per class delta AP for classification_duplicate_localisation errors. """
        if self.simplified:
            raise NotImplementedError('This category does not exist in simplified mode')
        self.compute('dAP_classification_duplicate_localisation')
        return self.cache['dAP_classification_duplicate_localisation'].copy()

    @property
    def dAP_background(self):
        """ Per class delta AP for background errors. """
        self.compute('dAP_background')
        return self.cache['dAP_background'].copy()

    @property
    def dAP_missed(self):
        """ Per class delta AP for missed errors. """
        self.compute('dAP_missed')
        return self.cache['dAP_missed'].copy()

    @property
    def dAP_fp(self):
        """ Per class delta AP for fp errors. """
        self.compute('dAP_fp')
        return self.cache['dAP_fp'].copy()

    @property
    def dAP_fn(self):
        """ Per class delta AP for fn errors. """
        self.compute('dAP_fn')
        return self.cache['dAP_fn'].copy()

    @property
    def errors(self):
        """
        Computes and returns the different error types. |br|
        This property returns your detection and annotation dataframe with an extra 'error' column,
        which explains the error type of that bounding box.
        If the bounding box is not an error, `pd.NA` is used.

        Return:
            tuple of 2 dataframes: (det, anno)
        """
        self.compute('error_detections', 'error_annotations')
        return self.cache['error_detections'].copy(), self.cache['error_annotations'].copy()


def find_errors(det, anno, pos_thresh, bg_thresh):
    det_idx = det.index
    anno_idx = anno.index
    det = det.reset_index(drop=True)
    anno = anno.reset_index(drop=True)

    dl = len(det_idx)
    anno_gt = anno[~anno.ignore]
    det_unmatched = det[~det.tp]

    # Create error df
    false_list = [False] * dl
    det_errors = pd.DataFrame({
        'classification': false_list,
        'duplicate': false_list,
        'localisation': false_list,
        'classification_duplicate': false_list,
        'classification_localisation': false_list,
        'duplicate_localisation': false_list,
        'classification_duplicate_localisation': false_list,
        'background': false_list,
        'index': det_idx,
        'anno': np.nan,
    })

    # No regular ground truth annotations -> all background errors
    if len(anno_gt.index) == 0:
        det_errors['background'] = det.fp
        return det_errors

    # Compute stats
    used_gt = anno_gt['detection'].notnull().values
    diff_cls = ~(util.np_col(det, 'class_label')[:, None] == util.np_col(anno_gt, 'class_label')[None, :])
    iou = np.asarray(stat.coordinates.iou(det, anno_gt))
    iou_unused = iou * used_gt[None, :]

    # Find error type
    def set_error_type(det, anno, error_type, duplicate=False):
        if duplicate or anno in used_gt_errors[error_type]:
            det_errors.loc[det, error_type] = pd.NA
        else:
            det_errors.at[det, error_type] = True
            det_errors.at[det, 'anno'] = anno_idx[anno]
            used_gt_errors[error_type].add(anno)

    used_gt_errors = defaultdict(set)
    for d in det_unmatched.itertuples():
        # First try to match unused GT, then all GTs
        # This means that a detection in a cluster of GT objects would rather be labeled as a localisation/classification error,
        # instead of being labeled as a duplicate (eg. detection has 65% IoU with used GT, but also 55% with unused GT -> use unused instead of used).
        best_idx = iou_unused[d.Index, :].argmax()
        if iou_unused[d.Index, best_idx] < bg_thresh:
            best_idx = iou[d.Index, :].argmax()
        best_iou = iou[d.Index, best_idx]

        # We only mark an error as duplicate if it is using a used GT and not if it is used by another previous unmatched det
        # The idea here is that eg. 2 mislocalised detections should not have the 2nd labeled as mislocalised+duplicate,
        # because solving the localisation error, might remove the duplication (eg. NMS)
        dup_error = used_gt[best_idx]
        cls_error = diff_cls[d.Index, best_idx]

        if best_iou < bg_thresh:
            det_errors.at[d.Index, 'background'] = True
        elif best_iou >= pos_thresh:
            if cls_error and dup_error:
                set_error_type(d.Index, best_idx, 'classification_duplicate', duplicate=True)
            elif cls_error:
                set_error_type(d.Index, best_idx, 'classification')
            elif dup_error:
                set_error_type(d.Index, best_idx, 'duplicate', duplicate=True)
            else:
                raise RuntimeError('Unkown error type!')
        else:
            if cls_error and dup_error:
                set_error_type(d.Index, best_idx, 'classification_duplicate_localisation', duplicate=True)
            elif cls_error:
                set_error_type(d.Index, best_idx, 'classification_localisation')
            elif dup_error:
                set_error_type(d.Index, best_idx, 'duplicate_localisation', duplicate=True)
            else:
                set_error_type(d.Index, best_idx, 'localisation')

    return det_errors.astype({
        'classification': 'boolean',
        'duplicate': 'boolean',
        'localisation': 'boolean',
        'classification_duplicate': 'boolean',
        'classification_localisation': 'boolean',
        'duplicate_localisation': 'boolean',
        'classification_duplicate_localisation': 'boolean',
        'background': 'boolean',
        'anno': 'Int64',
    })
