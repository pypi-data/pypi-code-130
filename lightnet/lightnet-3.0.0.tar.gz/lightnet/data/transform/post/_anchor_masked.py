#
#   Lightnet postprocessing for Masked Anchor based detectors (Darknet)
#   Copyright EAVISE
#

import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from lightnet.util import crop_mask, cwh_xyxy
from lightnet._compat import meshgrid_kw
from ._base import MultiScale

__all__ = ['GetMaskedAnchorBoxes', 'GetMultiScaleMaskedAnchorBoxes', 'GetMasks']
log = logging.getLogger(__name__)


class GetMaskedAnchorBoxes(nn.Module):
    """ Convert the output from masked anchor detection networks to an HBB tensor with mask coefficients. |br|
    This class is is meant to be used on the output of a :class:`~lightnet.network.head.DetectionMaskedAnchor` module.

    Args:
        conf_thresh (Number [0-1]): Confidence threshold to filter detections
        num_masks (int): The number of prototype masks that are used
        network_stride (int): Downsampling factors of the network (most lightnet networks have a `stride` attribute)
        anchors (ln.util.Anchors): single-scale list of anchor boxes

    Returns:
        torch.Tensor [Boxes x (7 + num_masks)]:
            **[batch_num, x_c, y_c, width, height, mask_coef_0, ..., mask_coef_N, confidence, class_id]** for every bounding box
    """
    def __init__(self, conf_thresh, num_masks, network_stride, anchors):
        super().__init__()
        self.conf_thresh = conf_thresh
        self.num_masks = num_masks
        self.network_stride = network_stride
        self.num_anchors = anchors.num_anchors
        self.anchors = anchors.as_output(network_stride)

    def forward(self, output):
        device = output.device
        nB, channels, nH, nW = output.shape
        nC = (channels // self.num_anchors) - 5 - self.num_masks

        # Get separate outputs
        box_output = output[:, :-self.num_masks*self.num_anchors].view(nB, self.num_anchors, -1, nH*nW)
        mask_output = output[:, -self.num_masks*self.num_anchors:].view(nB, self.num_anchors, self.num_masks, nH*nW).transpose(2, 3)

        lin_y, lin_x = torch.meshgrid(torch.arange(nH), torch.arange(nW), **meshgrid_kw)
        lin_x = lin_x.reshape(-1).to(device)
        lin_y = lin_y.reshape(-1).to(device)
        anchor_wh = self.anchors.reshape(1, self.num_anchors, 2, 1).to(device)

        # Compute max possible width/height network output, before the computed width/height would reach inf
        max_value = torch.tensor(1e35, dtype=box_output.dtype, device=box_output.device)
        max_value = (max_value / anchor_wh.max() / self.network_stride).log().floor()

        # Compute xc,yc, w,h, box_score on Tensor
        box_output = box_output.view(nB, self.num_anchors, -1, nH*nW)                               # -1 == 5+nC (we can drop feature maps if 1 class)
        box_output[:, :, 0, :].sigmoid_().add_(lin_x)                                               # X center
        box_output[:, :, 1, :].sigmoid_().add_(lin_y)                                               # Y center
        box_output[:, :, 2:4, :].clamp_(max=max_value).exp_().mul_(anchor_wh)                       # Width, Height
        box_output[:, :, 4, :].sigmoid_()                                                           # Box score

        # Compute class_score
        if nC > 1:
            with torch.no_grad():
                cls_scores = F.softmax(box_output[:, :, 5:, :], 2)
            cls_max, cls_max_idx = torch.max(cls_scores, 2)
            cls_max_idx = cls_max_idx.float()
            cls_max.mul_(box_output[:, :, 4, :])
        else:
            cls_max = box_output[:, :, 4, :]
            cls_max_idx = torch.zeros_like(cls_max)

        # Filter output boxes
        score_thresh = cls_max > self.conf_thresh
        if score_thresh.sum() == 0:
            return torch.empty(0, 7+self.num_masks, device=device)
        else:
            # Mask select boxes > conf_thresh
            coords = box_output.transpose(2, 3)[..., 0:4]
            coords = coords[score_thresh[..., None].expand_as(coords)].view(-1, 4)
            scores = cls_max[score_thresh]
            idx = cls_max_idx[score_thresh]

            # Get batch numbers of the detections
            batch_num = score_thresh.view(nB, -1)
            nums = torch.arange(1, nB+1, dtype=torch.long, device=batch_num.device)
            batch_num = (batch_num * nums[:, None])[batch_num] - 1

            # Get mask values
            mask_coef = mask_output.transpose(2, 3)
            mask_coef = mask_coef[score_thresh[..., None, :].expand_as(mask_coef)].view(-1, self.num_masks)

            return torch.cat(
                [
                    batch_num[:, None].float(),
                    coords * self.network_stride,
                    mask_coef,
                    scores[:, None],
                    idx[:, None],
                ],
                dim=1,
            )


class GetMultiScaleMaskedAnchorBoxes(MultiScale, GetMaskedAnchorBoxes):
    """ Convert the output from multiscale anchor detection networks to an HBB tensor with mask. |br|
    This class is is meant to be used on the output of multiple :class:`~lightnet.network.head.DetectionMaskedAnchor` modules.

    Args:
        conf_thresh (Number [0-1]): Confidence threshold to filter detections
        num_masks (int): The number of prototype masks that are used
        network_stride (list): Downsampling factors of the network (most lightnet networks have a `stride` attribute)
        anchors (list): 3D list representing anchor boxes (see :class:`lightnet.models.YoloV3`)

    Returns:
        torch.Tensor [Boxes x (7 + num_masks)]:
            **[batch_num, xc, yc, width, height, mask_coef_0, mask_coef_1, ..., mask_coef_M, confidence, class_id]** for every bounding box

    Note:
        The `anchors` and `network_stride` should be a list of different values for the different scales.
        When used, this post-processing class calls :class:`~lightnet.data.transform.GetMaskedAnchorBoxes` for different scales
        and thus uses different stride and anchors values.
    """
    GETBOXES = GetMaskedAnchorBoxes
    MULTISCALE_ARGS = ('network_stride', 'anchors')

    @staticmethod
    def _setup_multiscale_args(ms_args):
        """ Keep only scale specific anchors. """
        ms_args['anchors'] = ms_args['anchors'].split_scales()
        return MultiScale._setup_multiscale_args(ms_args)

    def _postprocess_multiscale_arg(self, ms_args, idx):
        """ Transform anchors to output relative tensors. """
        ms_args['num_anchors'] = ms_args['anchors'].num_anchors
        ms_args['anchors'] = ms_args['anchors'].as_output(ms_args['network_stride'])
        return ms_args


class GetMasks(nn.Module):
    """ Compute masks from prototype masks and coefficients.

    Args:
        mask_thresh (float or None): Threshold to binarize the resulting masks
        mask_stride (int): Input to mask dimension stride to rescale the output masks
        crop_masks (bool, optional): Whether to crop the masks to the box coordinates; Default **True**
    """
    def __init__(self, mask_thresh, mask_stride, crop_masks=True):
        super().__init__()
        self.mask_thresh = mask_thresh
        self.mask_stride = mask_stride
        self.crop_masks = crop_masks

    def forward(self, boxes, proto_masks=None):
        if proto_masks is None:
            # Allow this transform to work even when we use an HBB detector
            return boxes

        _, nM, mH, mW = proto_masks.shape

        # Compute masks
        mask_coef = boxes[:, 5:-2].view(-1, 1, nM)
        proto_masks = proto_masks[boxes[:, 0].long()].view(-1, nM, mH*mW)
        masks = (mask_coef @ proto_masks).view(-1, mH, mW).sigmoid_()

        # Crop masks
        if self.crop_masks:
            masks = crop_mask(masks, cwh_xyxy(boxes[:, 1:5]) / self.mask_stride)

        # Threshold masks
        if self.mask_thresh is not None:
            masks = masks > self.mask_thresh

        # Remove mask_coef
        cols = torch.zeros(boxes.shape[1], dtype=bool)
        cols[:5] = True
        cols[-2:] = True
        boxes = boxes[:, cols]

        return boxes, masks
