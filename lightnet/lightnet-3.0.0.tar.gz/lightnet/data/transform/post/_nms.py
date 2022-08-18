#
#   Lightnet related postprocessing
#   Copyright EAVISE
#
import logging
import numpy as np
import torch
import torch.nn as nn
from torchvision.ops import batched_nms, nms
from lightnet.util import cwh_xyxy
from lightnet._imports import bb


__all__ = ['NMS', 'NMSFast', 'NMSSoft', 'NMSSoftFast']
log = logging.getLogger(__name__)


class NMS(nn.Module):
    """ Performs non-maximal suppression on the bounding boxes, filtering boxes with a high overlap.
    This function can either work on a pytorch bounding box tensor or a brambox dataframe.

    Args:
        iou_thresh (Number [0-1]): Overlapping threshold to filter detections with non-maxima suppresion
        class_nms (bool, optional): Whether to perform nms per class; Default **True**
        memory_limit (int, optional): Threshold to the number of bounding boxes, before taking the slower NMS path, which consumes less memory (see Warning); Default **50000**
        reset_index (bool, optional): Whether to reset the index of the returned dataframe (dataframe only); Default **True**

    Warning:
        This transformation use :class:`torchvision.ops.batched_nms` in order to process all boxes from different images and classes together.
        However, this does mean that this the transformation might require a lot of (GPU) memory when computing the IoU of each box to all others ([boxes x boxes] tensor).

        In order to prevent consuming too much memory, we split the boxes tensor and perform NMS per image,
        if the total number of bounding boxes exceeds the number specified in the ``memory_limit`` args.
        Some rough testing showed that the default number of **50000** boxes, consumes up to 1GB of CUDA memory.

    Note:
        This post-processing function expects the input bounding boxes to be either a PyTorch tensor or a brambox dataframe.

        The PyTorch tensor needs to be one of the :ref:`api/data:GetBoxes` outputs.

        The brambox dataframe should be a detection dataframe,
        as it needs the x_top_left, y_top_left, width, height, confidence and class_label columns.
        If it contains a valid geos 'segmentation' column, we compute IoU using the segmentation data.

    Note:
        You can disable this transformation by setting the `iou_thresh` argument to zero.
    """
    def __init__(self, iou_thresh, *, class_nms=True, memory_limit=50000, reset_index=True, force_cpu=None, box_type=None):
        super().__init__()
        if force_cpu is not None:
            log.deprecated('The "force_cpu" argument is deprecated, as Lightnet now uses the cuda implementation of NMS from the torchvision package, which does not need this flag.')

        self.iou_thresh = iou_thresh
        self.class_nms = class_nms
        self.memory_limit = memory_limit
        self.reset_index = reset_index
        self.box_type = box_type.lower() if box_type is not None else None

    def forward(self, boxes):
        """ Runs NMS on the boxes.

        Args:
            boxes (torch.Tensor or pandas.Dataframe): bounding boxes

        Returns:
            torch.Tensor or pandas.Dataframe: filtered bounding boxes
        """
        if self.iou_thresh <= 0:
            return boxes

        if isinstance(boxes, torch.Tensor):
            if boxes.numel() == 0:
                return boxes
            else:
                coords = self._torch_coords(boxes)
                keep = self._torch_fast(coords, boxes) if boxes.shape[0] <= self.memory_limit else self._torch_slow(coords, boxes)
                return boxes[keep]
        else:
            return self._pandas(boxes)

    def _torch_coords(self, boxes):
        if (self.box_type == 'obb') or (self.box_type is None and boxes.shape[1] == 8):
            angle_abs = boxes[:, 5].abs()
            angle_sin = angle_abs.sin()
            angle_cos = angle_abs.cos()
            w2 = boxes[:, 3] / 2
            h2 = boxes[:, 4] / 2
            xmin = (boxes[:, 1] - h2 * angle_sin - w2 * angle_cos)
            xmax = (boxes[:, 1] + h2 * angle_sin + w2 * angle_cos)
            ymin = (boxes[:, 2] - h2 * angle_cos - w2 * angle_sin)
            ymax = (boxes[:, 2] + h2 * angle_cos + w2 * angle_sin)
            return torch.stack((xmin, ymin, xmax, ymax), dim=1)
        else:
            return cwh_xyxy(boxes[:, 1:5])

    def _torch_fast(self, coords, boxes):
        categories = boxes[:, 0].clone()
        if self.class_nms:
            classes = boxes[:, -1]
            categories = categories * classes.max() + classes

        return batched_nms(coords, boxes[:, -2], categories, self.iou_thresh)

    def _torch_slow(self, coords, boxes):
        batches = boxes[:, 0]
        keep = torch.zeros(boxes.shape[0], dtype=torch.bool, device=boxes.device)
        for batch in torch.unique(batches, sorted=False):
            mask = batches == batch
            mask_coords = coords[mask]
            mask_boxes = boxes[mask]
            if self.class_nms:
                keep_idx = batched_nms(mask_coords, mask_boxes[:, -2], mask_boxes[:, -1], self.iou_thresh)
                keep[mask] = torch.scatter(keep[mask], 0, keep_idx, 1)
            else:
                keep_idx = nms(mask_coords, mask_boxes[:, -2], self.iou_thresh)
                keep[mask] = torch.scatter(keep[mask], 0, keep_idx, 1)

        return keep

    @torch.jit.unused
    def _pandas(self, boxes):
        if len(boxes.index) == 0:
            return boxes
        boxes = boxes.groupby('image', group_keys=False, observed=True).apply(self._pandas_nms)
        if self.reset_index:
            return boxes.reset_index(drop=True)
        return boxes

    def _pandas_nms(self, boxes):
        boxes = boxes.sort_values('confidence', ascending=False)
        ious = np.asarray(bb.stat.coordinates.iou(boxes, boxes, bias=0))

        # Filter based on iou (and class)
        conflicting = np.triu(ious > self.iou_thresh, 1)
        if self.class_nms:
            classes = boxes['class_label'].values
            same_class = (classes[None, ...] == classes[..., None])
            conflicting = (conflicting & same_class)

        keep = np.zeros(conflicting.shape[0], dtype=np.bool)
        supress = np.zeros(conflicting.shape[0], dtype=np.bool)
        for i, row in enumerate(conflicting):
            if not supress[i]:
                keep[i] = True
                supress[row] = True

        return boxes[keep]


def NMSFast(*args, **kwargs):
    log.deprecated('Lightnet now uses the cuda implementation of NMS from the torchvision package, which is faster than both the NMS and NMSFast implementations. Simply use NMS')
    return NMS(*args, **kwargs)


class NMSSoft(nn.Module):
    """ Performs soft NMS with exponential decaying on the bounding boxes, as explained in :cite:`soft_nms`.
    This function can either work on a pytorch bounding box tensor or a brambox dataframe.

    Args:
        sigma (Number): Sensitivity value for the confidence rescaling (exponential decay)
        conf_thresh (Number [0-1], optional): Confidence threshold to filter the bounding boxes after decaying them; Default **0**
        class_nms (Boolean, optional): Whether to perform nms per class; Default **True**
        force_cpu (Boolean, optional): Whether to force a part of the computation on CPU (tensor only, see Note); Default **True**
        reset_index (Boolean, optional): Whether to reset the index of the returned dataframe (dataframe only); Default **True**

    Note:
        This post-processing function expects the input bounding boxes to be either a PyTorch tensor or a brambox dataframe.

        The PyTorch tensor needs to be formatted as follows: **[batch_num, x_tl, y_tl, x_br, y_br, confidence, class_id]** for every bounding box.
        This corresponds to the output from the GetBoxes classes available in lightnet.
        When using tensors you can optionally pass in extra tensors of the dimensions [Boxes, ...], which will be filtered as well.

        The brambox dataframe should be a detection dataframe,
        as it needs the x_top_left, y_top_left, width, height, confidence and class_label columns.
    """
    def __init__(self, sigma, *, conf_thresh=0, class_nms=True, force_cpu=True, reset_index=True):
        super().__init__()
        self.sigma = sigma
        self.conf_thresh = conf_thresh
        self.class_nms = class_nms
        self.force_cpu = force_cpu
        self.reset_index = reset_index

    def forward(self, boxes):
        """ Runs NMS on the boxes.

        Args:
            boxes (Tensor [Boxes x 7] or pandas.Dataframe): bounding boxes

        Returns:
            boxes (Tensor [Boxes x 7] or pandas.Dataframe): filtered bounding boxes
        """
        if isinstance(boxes, torch.Tensor):
            return self._torch(boxes)
        else:
            return self._pandas(boxes)

    def _torch(self, boxes):
        if boxes.numel() == 0:
            return boxes

        batches = boxes[:, 0]
        for batch in torch.unique(batches, sorted=False):
            mask = batches == batch
            boxes[mask, 5] = self._torch_nms(boxes[mask])

        if self.conf_thresh > 0:
            keep = boxes[:, 5] > self.conf_thresh
            return boxes[keep]

        return boxes

    def _torch_nms(self, boxes):
        if boxes.numel() == 0:
            return boxes

        bboxes = boxes[:, 1:5]
        scores = boxes[:, 5]
        classes = boxes[:, 6]

        # Sort coordinates by descending score
        scores, order = scores.sort(0, descending=True)
        x1, y1, x2, y2 = cwh_xyxy(bboxes[order], cat=False)

        # Compute dx and dy between each pair of boxes (these mat contain every pair twice...)
        dx = (x2.min(x2.t()) - x1.max(x1.t())).clamp(min=0)
        dy = (y2.min(y2.t()) - y1.max(y1.t())).clamp(min=0)

        # Compute iou
        intersections = dx * dy
        areas = (x2 - x1) * (y2 - y1)
        unions = (areas + areas.t()) - intersections
        ious = intersections / unions

        # Filter class
        if self.class_nms:
            classes = classes[order]
            same_class = (classes.unsqueeze(0) == classes.unsqueeze(1))
            ious *= same_class

        # Decay scores
        decay = torch.exp(-(ious ** 2) / self.sigma)
        if self.force_cpu:
            scores = scores.cpu()
            order = order.cpu()
            decay = decay.cpu()

        tempscores = scores.clone()
        for _ in range(scores.shape[0]):
            maxidx = tempscores.argmax()
            maxscore = tempscores[maxidx]
            if maxscore <= self.conf_thresh:
                break

            tempscores[maxidx] = -1
            mask = tempscores != -1
            tempscores[mask] *= decay[maxidx, mask]
            scores[mask] = tempscores[mask]

        scores = scores.to(boxes.device)
        order = order.to(boxes.device)
        return scores.scatter(0, order, scores)

    @torch.jit.unused
    def _pandas(self, boxes):
        if len(boxes.index) == 0:
            return boxes

        boxes = boxes.groupby('image', group_keys=False, observed=True).apply(self._pandas_nms)
        if self.conf_thresh > 0:
            boxes = boxes[boxes.confidence > self.conf_thresh].copy()
        if self.reset_index:
            return boxes.reset_index(drop=True)

        return boxes

    def _pandas_nms(self, boxes):
        boxes = boxes.sort_values('confidence', ascending=False)
        scores = boxes['confidence'].values
        ious = np.asarray(bb.stat.coordinates.iou(boxes, boxes, bias=0))

        # Filter class
        if self.class_nms:
            classes = boxes['class_label'].values
            same_class = (classes[None, ...] == classes[..., None])
            ious *= same_class

        # Decay scores
        decay = np.exp(-(ious ** 2) / self.sigma)
        tempscores = scores.copy()
        for _ in range(scores.shape[0]):
            maxidx = tempscores.argmax()
            maxscore = tempscores[maxidx]
            if maxscore <= self.conf_thresh:
                break

            tempscores[maxidx] = -1
            mask = tempscores != -1
            tempscores[mask] *= decay[maxidx, mask]
            scores[mask] = tempscores[mask]

        # Set scores back
        boxes['confidence'] = scores
        return boxes


class NMSSoftFast(NMSSoft):
    """ Faster version of SoftNMS which filters boxes with a high overlap, using exponential decay.
    This function can either work on a pytorch bounding box tensor or a brambox dataframe.

    This faster alternative makes a small "mistake" during NMS computation,
    in order to remove a necessary loop in the code, allowing it to run faster.
    The speed increase should be mostly notable when performing NMS with PyTorch tensors on the GPU.

    The difference is explained in the image below, where the boxes A and B overlap enough to be filtered out
    and the boxes B and C as well (but A and C do not). |br|
    Regular NMS will keep box C in this situation, because box B gets filtered out and is thus not there to remove C.
    Fast NMS will not do this and will only keep box A in this situation. |br|
    Depending on the use-case (closely clustered and overlapping objects), this might be a problem or not.

    .. figure:: /.static/api/nms-fast.*
       :width: 100%
       :alt: Fast NMS problem

       Regular NMS will keep both boxes A and C, but Fast NMS will only keep A in this example.

    Args:
        sigma (Number): Sensitivity value for the confidence rescaling (exponential decay)
        conf_thresh (Number [0-1], optional): Confidence threshold to filter the bounding boxes after decaying them; Default **0**
        class_nms (Boolean, optional): Whether to perform nms per class; Default **True**
        reset_index (Boolean, optional): Whether to reset the index of the returned dataframe (dataframe only); Default **True**

    Note:
        This post-processing function expects the input bounding boxes to be either a PyTorch tensor or a brambox dataframe.

        The PyTorch tensor needs to be formatted as follows: **[batch_num, x_tl, y_tl, x_br, y_br, confidence, class_id]** for every bounding box.
        This corresponds to the output from the GetBoxes classes available in lightnet.
        When using tensors you can optionally pass in extra tensors of the dimensions [Boxes, ...], which will be filtered as well.

        The brambox dataframe should be a detection dataframe,
        as it needs the x_top_left, y_top_left, width, height, confidence and class_label columns.
    """
    def __init__(self, sigma, *, conf_thresh=0, class_nms=True, reset_index=True):
        super(NMSSoft, self).__init__()
        self.sigma = sigma
        self.conf_thresh = conf_thresh
        self.class_nms = class_nms
        self.reset_index = reset_index

    def _torch_nms(self, boxes):
        if boxes.numel() == 0:
            return boxes

        bboxes = boxes[:, 1:5]
        scores = boxes[:, 5]
        classes = boxes[:, 6]

        # Sort coordinates by descending score
        scores, order = scores.sort(0, descending=True)
        x1, y1, x2, y2 = cwh_xyxy(bboxes[order], cat=False)

        # Compute dx and dy between each pair of boxes (these mat contain every pair twice...)
        dx = (x2.min(x2.t()) - x1.max(x1.t())).clamp(min=0)
        dy = (y2.min(y2.t()) - y1.max(y1.t())).clamp(min=0)

        # Compute iou
        intersections = dx * dy
        areas = (x2 - x1) * (y2 - y1)
        unions = (areas + areas.t()) - intersections
        ious = intersections / unions

        # Filter class
        if self.class_nms:
            classes = classes[order]
            same_class = (classes.unsqueeze(0) == classes.unsqueeze(1))
            ious *= same_class

        # Decay scores
        decay = ious.triu(1)
        decay = torch.exp(-(decay ** 2) / self.sigma).prod(0)
        scores *= decay
        return scores.scatter(0, order, scores)

    def _pandas_nms(self, boxes):
        boxes = boxes.sort_values('confidence', ascending=False)
        scores = boxes['confidence'].values
        ious = np.asarray(bb.stat.coordinates.iou(boxes, boxes, bias=0))

        # Filter class
        if self.class_nms:
            classes = boxes['class_label'].values
            same_class = (classes[None, ...] == classes[..., None])
            ious *= same_class

        # Decay scores
        decay = np.triu(ious, 1)
        decay = np.prod(np.exp(-(decay ** 2) / self.sigma), 0)
        scores *= decay

        # Set scores back
        boxes['confidence'] = scores
        return boxes
