import numpy as np
import pandas as pd
import pandera as pa
from pandera.typing import Series


def compute_overlap(boxes, query_boxes):
    N = boxes.shape[0]
    overlaps = np.zeros((N), dtype=np.float64)
    box_area = (query_boxes[2] - query_boxes[0]) * (
        query_boxes[3] - query_boxes[1]
    )
    for n in range(N):
        iw = min(boxes[n, 2], query_boxes[2]) - max(
            boxes[n, 0], query_boxes[0]
        )
        if iw > 0:
            ih = min(boxes[n, 3], query_boxes[3]) - max(
                boxes[n, 1], query_boxes[1]
            )
            if ih > 0:
                ua = np.float64(
                    (boxes[n, 2] - boxes[n, 0]) * (boxes[n, 3] - boxes[n, 1])
                    + box_area
                    - iw * ih
                )
                overlaps[n] = iw * ih / ua
    return overlaps


def check_if_true_or_false_positive(annotations, detections, iou_threshold):
    annotations = np.array(annotations, dtype=np.float64)
    scores = []
    false_positives = []
    true_positives = []
    detected_annotations = (
        []
    )  # a GT box should be mapped only one predicted box at most.
    for d in detections:
        scores.append(d[4])
        if len(annotations) == 0:
            false_positives.append(1)
            true_positives.append(0)
            continue
        overlaps = compute_overlap(annotations, d[:4])
        assigned_annotation = np.argmax(overlaps)
        max_overlap = overlaps[assigned_annotation]
        if (
            max_overlap >= iou_threshold
            and assigned_annotation not in detected_annotations
        ):
            false_positives.append(0)
            true_positives.append(1)
            detected_annotations.append(assigned_annotation)
        else:
            false_positives.append(1)
            true_positives.append(0)
    return scores, false_positives, true_positives


def _compute_ap(recall, precision):
    # correct AP calculation
    # first append sentinel values at the end
    mrec = np.concatenate(([0.0], recall, [1.0]))
    mpre = np.concatenate(([0.0], precision, [0.0]))

    # compute the precision envelope
    for i in range(mpre.size - 1, 0, -1):
        mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

    # to calculate area under PR curve, look for points
    # where X axis (recall) changes value
    i = np.where(mrec[1:] != mrec[:-1])[0]

    # and sum (\Delta recall) * prec
    ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])

    return ap


def get_real_annotations(table):
    res = dict()
    ids = table["image_filename"].values.astype(np.str)
    labels = table["class_name"].values.astype(np.str)
    xmin = table["x_min"].values.astype(np.float32)
    xmax = table["x_max"].values.astype(np.float32)
    ymin = table["y_min"].values.astype(np.float32)
    ymax = table["y_max"].values.astype(np.float32)

    for i in range(len(ids)):
        id = ids[i]
        label = labels[i]
        if id not in res:
            res[id] = dict()
        if label not in res[id]:
            res[id][label] = []
        box = [xmin[i], ymin[i], xmax[i], ymax[i]]
        res[id][label].append(box)
    return res


def get_detections(table):
    res = dict()
    ids = table["image_filename"].values.astype(np.str)
    labels = table["class_name"].values.astype(np.str)
    scores = table["confidence_score"].values.astype(np.float32)
    xmin = table["x_min"].values.astype(np.float32)
    xmax = table["x_max"].values.astype(np.float32)
    ymin = table["y_min"].values.astype(np.float32)
    ymax = table["y_max"].values.astype(np.float32)

    for i in range(len(ids)):
        id = ids[i]
        label = labels[i]
        if id not in res:
            res[id] = dict()
        if label not in res[id]:
            res[id][label] = []
        box = [xmin[i], ymin[i], xmax[i], ymax[i], scores[i]]
        res[id][label].append(box)
    return res


class GroundTruthSchema(pa.SchemaModel):
    image_filename: Series[str] = pa.Field(check_name=True, nullable=False)
    class_name: Series[str] = pa.Field(check_name=True, nullable=False)
    x_min: Series[float] = pa.Field(check_name=True, nullable=False)
    y_min: Series[float] = pa.Field(check_name=True, nullable=False)
    x_max: Series[float] = pa.Field(check_name=True, nullable=False)
    y_max: Series[float] = pa.Field(check_name=True, nullable=False)


class DetectionsSchema(pa.SchemaModel):
    image_filename: Series[str] = pa.Field(check_name=True, nullable=False)
    class_name: Series[str] = pa.Field(check_name=True, nullable=False)
    confidence_score: Series[float] = pa.Field(
        gt=0, check_name=True, nullable=False
    )
    x_min: Series[float] = pa.Field(check_name=True, nullable=False)
    y_min: Series[float] = pa.Field(check_name=True, nullable=False)
    x_max: Series[float] = pa.Field(check_name=True, nullable=False)
    y_max: Series[float] = pa.Field(check_name=True, nullable=False)


def mean_average_precision_for_boxes(
    ground_truth_dataframe: pd.DataFrame,
    detections_dataframe: pd.DataFrame,
    iou_threshold=0.5,
    conf_threshold=0.6,
    exclude_not_in_annotations=False,
    verbose=True,
):
    GroundTruthSchema.validate(ground_truth_dataframe)
    DetectionsSchema.validate(detections_dataframe)

    valid = ground_truth_dataframe[
        ["image_filename", "class_name", "x_min", "x_max", "y_min", "y_max"]
    ]
    preds = detections_dataframe[
        [
            "image_filename",
            "class_name",
            "confidence_score",
            "x_min",
            "x_max",
            "y_min",
            "y_max",
        ]
    ]
    preds = preds[preds["confidence_score"] > conf_threshold]
    ann_unique = valid["image_filename"].unique()
    preds_unique = preds["image_filename"].unique()

    if verbose:
        print("Number of files in annotations: {}".format(len(ann_unique)))
        print("Number of files in predictions: {}".format(len(preds_unique)))

    # Exclude files not in annotations!
    if exclude_not_in_annotations:
        preds = preds[preds["image_filename"].isin(ann_unique)]
        preds_unique = preds["image_filename"].unique()
        if verbose:
            print(
                "Number of files in detection after reduction: {}".format(
                    len(preds_unique)
                )
            )

    unique_classes = valid["class_name"].unique().astype(np.str)
    if verbose:
        print("Unique classes: {}".format(len(unique_classes)))

    all_detections = get_detections(preds)
    all_annotations = get_real_annotations(valid)
    if verbose:
        print("Detections length: {}".format(len(all_detections)))
        print("Annotations length: {}".format(len(all_annotations)))

    average_precisions = {}
    for _, label in enumerate(sorted(unique_classes)):

        # Negative class
        if str(label) == "nan" or "":
            continue

        false_positives = []
        true_positives = []
        scores = []
        num_annotations = 0.0

        for i in range(len(ann_unique)):
            detections = []
            annotations = []
            id_ = ann_unique[i]
            if id_ in all_detections:
                if label in all_detections[id_]:
                    detections = all_detections[id_][label]
            if id_ in all_annotations:
                if label in all_annotations[id_]:
                    annotations = all_annotations[id_][label]

            if len(detections) == 0 and len(annotations) == 0:
                continue

            num_annotations += len(annotations)

            scr, fp, tp = check_if_true_or_false_positive(
                annotations, detections, iou_threshold
            )
            scores += scr
            false_positives += fp
            true_positives += tp

        if num_annotations == 0:
            average_precisions[label] = 0, 0
            continue

        false_positives = np.array(false_positives)
        true_positives = np.array(true_positives)
        scores = np.array(scores)

        # sort by score
        indices = np.argsort(-scores)
        false_positives = false_positives[indices]
        true_positives = true_positives[indices]

        # compute false positives and true positives
        false_positives = np.cumsum(false_positives)
        true_positives = np.cumsum(true_positives)

        # compute recall and precision
        recall = true_positives / num_annotations
        precision = true_positives / np.maximum(
            true_positives + false_positives, np.finfo(np.float64).eps
        )

        # compute average precision
        average_precision = _compute_ap(recall, precision)
        average_precisions[label] = (
            average_precision,
            num_annotations,
            precision,
            recall,
        )
        if verbose:
            s1 = "{:30s} | {:.6f} | {:7d}".format(
                label, average_precision, int(num_annotations)
            )
            print(s1)

    present_classes = 0
    precision = 0
    for label, (
        average_precision,
        num_annotations,
        _,
        _,
    ) in average_precisions.items():
        if num_annotations > 0:
            present_classes += 1
            precision += average_precision
    mean_ap = precision / present_classes
    if verbose:
        print("mAP: {:.6f}".format(mean_ap))
    return mean_ap, average_precisions
