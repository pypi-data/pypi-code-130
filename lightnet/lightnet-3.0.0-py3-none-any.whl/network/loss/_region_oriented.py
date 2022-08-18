#
#   OrientedRegionLoss
#   Copyright EAVISE
#
import logging
import math
import torch
import torch.nn as nn
import brambox as bb
from lightnet.util import iou_bb_cwha
from lightnet._compat import meshgrid_kw
from ._base import Loss, MultiScale

__all__ = ['OrientedRegionLoss', 'MultiScaleOrientedRegionLoss']
log = logging.getLogger(__name__)


class OrientedRegionLoss(Loss):
    """ Computes the region loss for oriented anchor detection networks. |br|
    This loss is is meant to be used on the output of a :class:`~lightnet.network.head.DetectionOrientedAnchor` module,
    together with a brambox dataframe of target annotations.

    Args:
        num_classes (int): number of classes to detect
        anchors (ln.util.Anchors): single-scale list of anchor boxes with angles
        network_stride (int): Downsampling factors of the network (most lightnet networks have a `stride` attribute)
        seen (optional, torch.Tensor): How many images the network has already been trained on; Default **0**
        coord_scale (optional, float): weight of bounding box coordinates; Default **1.0**
        noobject_scale (optional, float): weight of regions without target boxes; Default **1.0**
        object_scale (optional, float): weight of regions with target boxes; Default **5.0**
        class_scale (optional, float): weight of categorical predictions; Default **1.0**
        max_angle (float, optional): Maximum angle deviation the network can predict (in radians); Default **PI/4 (45deg)**
        iou_thresh (optional, float): minimum iou between a predicted box and ground truth for them to be considered matching; Default **0.6**
        coord_prefill (optional, int): This parameter controls for how many training samples the network will prefill the target coordinates, biassing the network to predict the center at **.5,.5**; Default **12800**

    Note:
        We use the HBB IoU in order to compute which detections match the annotations, as this is faster.
        In order to compute the best matching anchor for each annotation,
        we replace the OBB IoU with the L2 distance of the normalized `width`, `height` and `angle` features.
    """
    VALUES = ('total', 'conf', 'coord', 'angle', 'class')
    ENABLE_REDUCTION = True

    def __init__(
        self,
        num_classes,
        anchors,
        network_stride,
        seen=0,
        coord_scale=1.0,
        angle_scale=1.0,
        noobject_scale=1.0,
        object_scale=5.0,
        class_scale=1.0,
        max_angle=math.pi/4,
        iou_thresh=0.6,
        coord_prefill=12800,
    ):
        super().__init__()
        self.num_classes = num_classes
        self.num_anchors = anchors.num_anchors
        self.anchors = anchors.as_output(network_stride)
        self.anchors_max = self.anchors.abs().max(dim=0)[0]
        self.network_stride = network_stride
        self.register_buffer('seen', torch.tensor(seen))
        self.coord_scale = coord_scale
        self.angle_scale = angle_scale
        self.noobject_scale = noobject_scale
        self.object_scale = object_scale
        self.class_scale = class_scale
        self.max_angle = max_angle
        self.iou_thresh = iou_thresh
        self.coord_prefill = coord_prefill

        self.mse = nn.MSELoss(reduction='none')
        self.cel = nn.CrossEntropyLoss(reduction='none')

    def extra_repr(self):
        anchors = ' '.join(f'[{a[0]:.5g}, {a[1]:.5g}, {a[2]:.5g}]' for a in self.anchors)
        return (
            f'classes={self.num_classes}, network_stride={self.network_stride}, IoU threshold={self.iou_thresh}, seen={self.seen.item()}\n'
            f'coord_scale={self.coord_scale}, angle_scale={self.angle_scale}, object_scale={self.object_scale}, noobject_scale={self.noobject_scale}, class_scale={self.class_scale}\n'
            f'anchors={anchors}'
        )

    def forward(self, output, target, seen=None):
        """ Compute Region loss.

        Args:
            output (torch.autograd.Variable): Output from the network
            target (brambox annotation dataframe): Brambox annotations with a "segmentation" column
            seen (int, optional): How many images the network has already been trained on; Default **Add batch_size to previous seen value**
        """
        # Parameters
        nB = output.data.size(0)
        nA = self.num_anchors
        nC = self.num_classes
        nH = output.data.size(2)
        nW = output.data.size(3)
        nPixels = nH * nW
        device = output.device
        if seen is not None:
            self.seen = torch.tensor(seen)
        elif self.training:
            self.seen += nB

        # Get x,y,w,h,a,conf,cls
        output = output.view(nB, nA, -1, nPixels)
        coord = torch.empty_like(output[:, :, :4])
        coord[:, :, :2] = output[:, :, :2].sigmoid()    # tx,ty
        coord[:, :, 2:4] = output[:, :, 2:4]            # tw,th
        angle = output[:, :, 4].tanh()
        conf = output[:, :, 5].sigmoid()
        if nC > 1:
            cls = output[:, :, 6:].reshape(nB*nA, nC, nPixels).transpose(1, 2).reshape(-1, nC)

        with torch.no_grad():
            # Create prediction boxes
            pred_boxes = torch.FloatTensor(nB*nA*nPixels, 5)

            lin_y, lin_x = torch.meshgrid(torch.arange(nH), torch.arange(nW), **meshgrid_kw)
            lin_x = lin_x.reshape(-1).to(device)
            lin_y = lin_y.reshape(-1).to(device)
            anchor_wh = self.anchors[:, :2].reshape(nA, 2, 1).to(device)
            anchor_a = self.anchors[:, 2].reshape(nA, 1).to(device)

            # Compute max possible width/height network output, before the computed width/height would reach inf
            max_value = torch.tensor(1e35, dtype=pred_boxes.dtype, device=pred_boxes.device)
            max_value = (max_value / anchor_wh.max()).log().floor()

            # Get prediction coordinates
            pred_boxes[:, 0] = (coord[:, :, 0].detach() + lin_x).view(-1)
            pred_boxes[:, 1] = (coord[:, :, 1].detach() + lin_y).view(-1)
            pred_boxes[:, 2:4] = (coord[:, :, 2:4].detach().clamp(max=max_value).exp() * anchor_wh).view(-1, 2)
            pred_boxes[:, 4] = (angle.detach() * self.max_angle + anchor_a).view(-1)
            pred_boxes = pred_boxes.cpu()

            # Get target values
            coord_mask, angle_mask, conf_mask, cls_mask, tcoord, tangle, tconf, tcls = self.build_targets(pred_boxes, target, nB, nH, nW)
            coord_mask = coord_mask.expand_as(tcoord).to(device).sqrt()
            angle_mask = angle_mask.to(device).sqrt()
            conf_mask = conf_mask.to(device).sqrt()
            tcoord = tcoord.to(device)
            tangle = tangle.to(device)
            tconf = tconf.to(device)
            if nC > 1:
                tcls = tcls[cls_mask].view(-1).long().to(device)
                cls_mask = cls_mask.view(-1, 1).repeat(1, nC).to(device)
                cls = cls[cls_mask].view(-1, nC)

        # Confidence loss
        if self.object_scale == 0 and self.noobject_scale == 0:
            self.loss_conf = torch.tensor([0.0] * nB, device=device)
        else:
            self.loss_conf = torch.nn.functional.mse_loss(conf*conf_mask, tconf*conf_mask, reduction='none')
            self.loss_conf = self.loss_conf.sum(dim=tuple(range(1, self.loss_conf.ndim))) / 2

        # Coordinate loss
        if self.coord_scale == 0:
            self.loss_coord = torch.tensor([0.0] * nB, device=device)
        else:
            self.loss_coord = torch.nn.functional.mse_loss(coord*coord_mask, tcoord*coord_mask, reduction='none')
            self.loss_coord = self.coord_scale * self.loss_coord.sum(dim=tuple(range(1, self.loss_coord.ndim))) / 2

        # Angle loss
        if self.angle_scale == 0:
            self.loss_angle = torch.tensor([0.0] * nB, device=device)
        else:
            self.loss_angle = torch.nn.functional.mse_loss(angle*angle_mask, tangle*angle_mask, reduction='none')
            self.loss_angle = self.angle_scale * self.loss_angle.sum(dim=tuple(range(1, self.loss_angle.ndim))) / 2

        # Class loss
        if self.class_scale == 0 or nC == 1 or tcls.numel() == 0:
            self.loss_class = torch.tensor([0.0] * nB, device=device)
        else:
            self.loss_class = torch.nn.functional.cross_entropy(cls, tcls, reduction='none')
            self.loss_class = self.class_scale * self.loss_class.sum(dim=tuple(range(1, self.loss_class.ndim)))

        # Total loss
        self.loss_total = self.loss_conf + self.loss_coord + self.loss_angle + self.loss_class
        return self.loss_total

    def build_targets(self, pred_boxes, ground_truth, nB, nH, nW):
        """ Compare prediction boxes and ground truths, convert ground truths to network output tensors """
        # Parameters
        nA = self.num_anchors
        nAnchors = nA*nH*nW
        nPixels = nH*nW

        # Ground Truth
        if 'angle' not in ground_truth.columns:
            ground_truth = bb.util.BoundingBoxTransformer(ground_truth).get_obb()

        # Tensors
        coord_mask = torch.zeros(nB, nA, nH, nW)
        angle_mask = torch.zeros(nB, nA, nH, nW)
        conf_mask = torch.ones(nB, nA, nH, nW) * self.noobject_scale
        cls_mask = torch.zeros(nB, nA, nH, nW, dtype=torch.bool)
        tcoord = torch.zeros(nB, nA, 4, nH, nW)
        tangle = torch.zeros(nB, nA, nH, nW)
        tconf = torch.zeros(nB, nA, nH, nW)
        tcls = torch.zeros(nB, nA, nH, nW)

        if self.training and self.seen < self.coord_prefill:
            coord_mask.fill_(.01 / self.coord_scale)
            angle_mask.fill_(.01 / self.angle_scale)
            tcoord[:, :, 0].fill_(0.5)
            tcoord[:, :, 1].fill_(0.5)

        # Loop over GT
        for b, gt_filtered in ground_truth.groupby('batch_number', sort=False):
            cur_pred_boxes = pred_boxes[b*nAnchors:(b+1)*nAnchors]

            # Create ground_truth tensor gt
            gt = torch.from_numpy(
                gt_filtered[['x_top_left', 'y_top_left', 'width', 'height', 'angle']].to_numpy(copy=True),
            ).float()

            # Convert from topleft -> center
            w2 = gt[:, 2] / 2
            h2 = gt[:, 3] / 2
            sin = gt[:, 4].sin()
            cos = gt[:, 4].cos()
            gt[:, 0] += w2 * cos + h2 * sin
            gt[:, 1] += h2 * cos - w2 * sin

            # Divide coordinates by stride
            gt[:, :4] /= self.network_stride

            # Set confidence mask of matching detections to 0
            # NOTE: We use iou_bb which is suboptimal (horizontal), but implementing a real iou for rotated rects is complicated
            iou_gt_pred = iou_bb_cwha(gt, cur_pred_boxes)
            mask = (iou_gt_pred > self.iou_thresh).sum(0) >= 1
            conf_mask[b][mask.view_as(conf_mask[b])] = 0

            # Find best anchor for each gt
            # NOTE: Because implementing IoU for rotated rects is cumbersome, we try a different approach with an L2 distance
            iou_gt_anchors = torch.cdist(
                (gt[:, 2:] / self.anchors_max).unsqueeze(0),
                (self.anchors / self.anchors_max).unsqueeze(0),
                2,
            ).squeeze(0)
            _, best_anchors = iou_gt_anchors.max(1)

            # Set masks and target values for each gt
            nGT = gt.shape[0]
            gi = gt[:, 0].clamp(0, nW-1).long()
            gj = gt[:, 1].clamp(0, nH-1).long()

            conf_mask[b, best_anchors, gj, gi] = self.object_scale
            tconf[b, best_anchors, gj, gi] = iou_gt_pred.view(nGT, nA, nH, nW)[torch.arange(nGT), best_anchors, gj, gi]
            coord_mask[b, best_anchors, gj, gi] = 2 - torch.clamp(gt[:, 2] * gt[:, 3] / nPixels, max=1.5)
            tcoord[b, best_anchors, 0, gj, gi] = gt[:, 0] - gi.float()
            tcoord[b, best_anchors, 1, gj, gi] = gt[:, 1] - gj.float()
            tcoord[b, best_anchors, 2:4, gj, gi] = (gt[:, 2:4] / self.anchors[best_anchors, 0:2]).log()
            angle_mask[b, best_anchors, gj, gi] = 1
            tangle[b, best_anchors, gj, gi] = (gt[:, 4] - self.anchors[best_anchors, 2]) / self.max_angle
            cls_mask[b, best_anchors, gj, gi] = 1
            tcls[b, best_anchors, gj, gi] = torch.from_numpy(gt_filtered.class_id.values).float()

            # Set masks of ignored to zero
            if gt_filtered.ignore.any():
                ignore_mask = torch.from_numpy(gt_filtered.ignore.values)
                gi = gi[ignore_mask]
                gj = gj[ignore_mask]
                best_anchors = best_anchors[ignore_mask]

                conf_mask[b, best_anchors, gj, gi] = 0
                coord_mask[b, best_anchors, gj, gi] = 0
                cls_mask[b, best_anchors, gj, gi] = 0

        return (
            coord_mask.view(nB, nA, 1, nPixels),
            angle_mask.view(nB, nA, nPixels),
            conf_mask.view(nB, nA, nPixels),
            cls_mask.view(nB, nA, nPixels),
            tcoord.view(nB, nA, 4, nPixels),
            tangle.view(nB, nA, nPixels),
            tconf.view(nB, nA, nPixels),
            tcls.view(nB, nA, nPixels),
        )


class MultiScaleOrientedRegionLoss(MultiScale, OrientedRegionLoss):
    """ Computes the region loss for multiscale oriented anchor detection networks. |br|
    This class is is meant to be used on the output of multiple :class:`~lightnet.network.head.DetectionOrientedAnchor` modules,
    together with a brambox dataframe of target annotations.

    Args:
        num_classes (int): number of classes to detect
        anchors (ln.util.Anchors): multi-scale list of anchor boxes with angles
        network_stride (list): Downsampling factors of the network (most lightnet networks have a `stride` attribute)
        seen (optional, torch.Tensor): How many images the network has already been trained on; Default **0**
        coord_scale (optional, float): weight of bounding box coordinates; Default **1.0**
        noobject_scale (optional, float): weight of regions without target boxes; Default **1.0**
        object_scale (optional, float): weight of regions with target boxes; Default **5.0**
        class_scale (optional, float): weight of categorical predictions; Default **1.0**
        max_angle (float, optional): Maximum angle deviation the network can predict (in radians); Default **PI/4 (45deg)**
        iou_thresh (optional, float): minimum iou between a predicted box and ground truth for them to be considered matching; Default **0.6**
        coord_prefill (optional, int): This parameter controls for how many training samples the network will prefill the target coordinates, biassing the network to predict the center at **.5,.5**; Default **12800**

    Note:
        All parameters are the same as :class:`~lightnet.network.loss.OrientedRegionLoss`, except for `anchors` and `stride`. |br|
        These 2 parameters need separate values for each different network output scale and thus need to be lists of the original parameter.
    """
    LOSS = OrientedRegionLoss
    MULTISCALE_ARGS = ('anchors', 'network_stride')

    @staticmethod
    def _setup_multiscale_args(ms_args):
        """ Keep only scale specific anchors. """
        ms_args['anchors'] = ms_args['anchors'].split_scales()
        return MultiScale._setup_multiscale_args(ms_args)

    def _postprocess_multiscale_arg(self, ms_args, idx):
        """ Transform anchors to output relative tensors. """
        ms_args['num_anchors'] = ms_args['anchors'].num_anchors
        ms_args['anchors'] = ms_args['anchors'].as_output(ms_args['network_stride'])
        ms_args['anchors_max'] = ms_args['anchors'].abs().max(dim=0)[0]
        return ms_args

    def _setup_forward_kwargs(self, output, target, kwargs):
        """ Setup seen argument because otherwise each scale forward run will increase its value. """
        if 'seen' not in kwargs:
            kwargs['seen'] = self.seen.item() + output[0].shape[0]
        return kwargs
