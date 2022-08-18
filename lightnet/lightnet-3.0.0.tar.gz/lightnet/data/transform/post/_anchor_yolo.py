#
#   Lightnet postprocessing for Anchor based detectors (Darknet)
#   Copyright EAVISE
#

import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from lightnet._compat import meshgrid_kw
from ._base import MultiScale

__all__ = ['GetAnchorBoxes', 'GetMultiScaleAnchorBoxes', 'GetDarknetBoxes', 'GetMultiScaleDarknetBoxes']
log = logging.getLogger(__name__)


class GetAnchorBoxes(nn.Module):
    """ Convert the output from anchor detection networks to an HBB tensor. |br|
    This class is is meant to be used on the output of a :class:`~lightnet.network.head.DetectionAnchor` module.

    Args:
        conf_thresh (Number [0-1]): Confidence threshold to filter detections
        network_stride (int): Downsampling factors of the network (most lightnet networks have a `stride` attribute)
        anchors (ln.util.Anchors): single-scale list of anchor boxes

    Returns:
        torch.Tensor [Boxes x 7]:
            **[batch_num, x_c, y_c, width, height, confidence, class_id]** for every bounding box
    """
    def __init__(self, conf_thresh, network_stride, anchors):
        super().__init__()
        self.conf_thresh = torch.tensor(conf_thresh)
        self.network_stride = torch.tensor(network_stride)
        self.num_anchors = anchors.num_anchors
        self.anchors = anchors.as_output(network_stride)

    def forward(self, network_output):
        device = network_output.device
        batch, channels, h, w = network_output.shape
        num_classes = (channels // self.num_anchors) - 5

        lin_y, lin_x = torch.meshgrid(torch.arange(h), torch.arange(w), **meshgrid_kw)
        lin_x = lin_x.reshape(-1).to(device)
        lin_y = lin_y.reshape(-1).to(device)
        anchor_wh = self.anchors.reshape(1, self.num_anchors, 2, 1).to(device)

        # Compute max possible width/height network output, before the computed width/height would reach inf
        max_value = torch.tensor(1e35, dtype=network_output.dtype, device=network_output.device)
        max_value = (max_value / anchor_wh.max() / self.network_stride).log().floor()

        # Compute xc,yc, w,h, box_score on Tensor
        network_output = network_output.view(batch, self.num_anchors, -1, h*w)                                  # -1 == 5+num_classes (we can drop feature maps if 1 class)
        network_output[:, :, 0, :].sigmoid_().add_(lin_x).mul_(self.network_stride)                             # X center
        network_output[:, :, 1, :].sigmoid_().add_(lin_y).mul_(self.network_stride)                             # Y center
        network_output[:, :, 2:4, :].clamp_(max=max_value).exp_().mul_(anchor_wh).mul_(self.network_stride)     # Width, Height
        network_output[:, :, 4, :].sigmoid_()                                                                   # Box score

        # Compute class_score
        if num_classes > 1:
            with torch.no_grad():
                cls_scores = F.softmax(network_output[:, :, 5:, :], 2)
            cls_max, cls_max_idx = torch.max(cls_scores, 2)
            cls_max_idx = cls_max_idx.float()
            cls_max.mul_(network_output[:, :, 4, :])
        else:
            cls_max = network_output[:, :, 4, :]
            cls_max_idx = torch.zeros_like(cls_max)

        # Filter output boxes
        score_thresh = cls_max > self.conf_thresh
        if score_thresh.sum() == 0:
            return torch.empty(0, 7, device=device)
        else:
            # Mask select boxes > conf_thresh
            coords = network_output.transpose(2, 3)[..., 0:4]
            coords = coords[score_thresh[..., None].expand_as(coords)].view(-1, 4)
            scores = cls_max[score_thresh]
            idx = cls_max_idx[score_thresh]

            # Get batch numbers of the detections
            batch_num = score_thresh.view(batch, -1)
            nums = torch.arange(1, batch+1, dtype=torch.long, device=batch_num.device)
            batch_num = (batch_num * nums[:, None])[batch_num] - 1

            return torch.cat([batch_num[:, None].float(), coords, scores[:, None], idx[:, None]], dim=1)


class GetMultiScaleAnchorBoxes(MultiScale, GetAnchorBoxes):
    """ Convert the output from multiscale anchor detection networks to an HBB tensor. |br|
    This class is is meant to be used on the output of multiple :class:`~lightnet.network.head.DetectionAnchor` modules.

    Args:
        conf_thresh (Number [0-1]): Confidence threshold to filter detections
        network_stride (list): Downsampling factors of the network (most lightnet networks have a `stride` attribute)
        anchors (ln.util.Anchors): multi-scale list of anchor boxes

    Returns:
        Tensor [Boxes x 7]:
            **[batch_num, x_tl, y_tl, x_br, y_br, confidence, class_id]** for every bounding box

    Note:
        The `anchors` and `network_stride` should be a list of different values for the different scales.
        When used, this post-processing class calls :class:`~lightnet.data.transform.GetDarknetBoxes` for different scales
        and thus uses different network_stride and anchors values.

    Warning:
        This post-processing function is not entirely equivalent to the Darknet implementation! |br|
        We just execute the regular :class:`~lightnet.data.transform.GetBoundingBoxes` at multiple scales (different strides and anchors),
        and as such did not implement overlapping class labels.
    """
    GETBOXES = GetAnchorBoxes
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


def GetDarknetBoxes(*args, **kwargs):
    log.deprecated_once('GetDarknetBoxes is renamed to GetAnchorBoxes.')
    return GetAnchorBoxes(*args, **kwargs)


def GetMultiScaleDarknetBoxes(*args, **kwargs):
    log.deprecated_once('GetMultiScaleDarknetBoxes is renamed to GetMultiScaleAnchorBoxes.')
    return GetMultiScaleAnchorBoxes(*args, **kwargs)
