#
#   Darknet RegionLoss combined with Yolact Masks
#   Copyright EAVISE
#
import logging
import numpy as np
import torch
from lightnet.util import iou_cwh, iou_wh, crop_mask, tlwh_xyxy
from lightnet._imports import bb
from lightnet._compat import meshgrid_kw
from ._base import Loss, MultiScale

__all__ = ['MaskedRegionLoss', 'MultiScaleMaskedRegionLoss']
log = logging.getLogger(__name__)


class MaskedRegionLoss(Loss):
    """ Computes the region loss for anchor detection networks. |br|
    This loss is is meant to be used on the output of a :class:`~lightnet.network.head.DetectionAnchor` module,
    together with a brambox dataframe of target annotations.

    Args:
        num_classes (int): number of classes to detect
        anchors (ln.util.Anchors): single-scale list of anchor boxes
        network_stride (int): Downsampling factors of the network (most lightnet networks have a `stride` attribute)
        coord_scale (float, optional): weight of bounding box coordinates; Default **1.0**
        noobject_scale (float, optional): weight of regions without target boxes; Default **1.0**
        object_scale (float, optional): weight of regions with target boxes; Default **5.0**
        class_scale (float, optional): weight of categorical predictions; Default **1.0**
        mask_scale (float, optional): weight for the mask loss; Default **1.0**
        max_masks (int, optional): Maximum number of masks to train on in 1 batch (reduce GPU usage); Default **100**
        max_rescale (float 0-1, optional): How much to rescale the mask loss of each object with regards to its bounding box size (0 = no rescaling | 1 = max rescaling); Default **1.0**
        iou_thresh (float, optional): minimum iou between a predicted box and ground truth for them to be considered matching; Default **0.6**
        coord_prefill (int, optional): This parameter controls for how many training samples the network will prefill the target coordinates, biassing the network to predict the center at **.5,.5**; Default **12800**
        seen (torch.Tensor, optional): How many images the network has already been trained on; Default **0**
    """
    VALUES = ('total', 'conf', 'coord', 'mask', 'class')
    ENABLE_REDUCTION = True

    def __init__(
        self,
        num_classes,
        anchors,
        network_stride,
        coord_scale=1.0,
        noobject_scale=1.0,
        object_scale=5.0,
        class_scale=1.0,
        mask_scale=1.0,
        max_masks=100,
        mask_rescale=1.0,
        iou_thresh=0.6,
        coord_prefill=12800,
        seen=0,
    ):
        super().__init__()
        self.num_classes = num_classes
        self.num_anchors = anchors.num_anchors
        self.anchors = anchors.as_output(network_stride)
        self.network_stride = network_stride
        self.coord_scale = coord_scale
        self.noobject_scale = noobject_scale
        self.object_scale = object_scale
        self.class_scale = class_scale
        self.mask_scale = mask_scale
        self.max_masks = max_masks
        self.mask_rescale = max(min(mask_rescale, 1.0), 0.0)
        self.iou_thresh = iou_thresh
        self.coord_prefill = coord_prefill
        self.register_buffer('seen', torch.tensor(seen))

    def extra_repr(self):
        anchors = ' '.join(f'[{a[0]:.5g}, {a[1]:.5g}]' for a in self.anchors)
        return (
            f'classes={self.num_classes}, network_stride={self.network_stride}, IoU threshold={self.iou_thresh}, seen={self.seen.item()}\n'
            f'coord_scale={self.coord_scale}, object_scale={self.object_scale}, noobject_scale={self.noobject_scale}, class_scale={self.class_scale}, mask_scale={self.mask_scale}\n'
            f'max_masks={self.max_masks}, mask_rescale={self.mask_rescale}\n'
            f'anchors={anchors}'
        )

    def forward(self, output, target, *, seen=None):
        """ Compute Region loss.

        Args:
            output (torch.autograd.Variable): Output from the network
            target (brambox annotation dataframe): Brambox annotations with segmentation data.
            seen (int, optional): How many images the network has already been trained on; Default **Add batch_size to previous seen value**
        """
        output, proto_masks = output

        # Parameters
        nA = self.num_anchors
        nC = self.num_classes
        nB, _, nH, nW = output.shape
        _, nM, mH, mW = proto_masks.shape
        nPixels = nH * nW
        device = output.device
        if seen is not None:
            self.seen = torch.tensor(seen)
        elif self.training:
            self.seen += nB

        # Get separate outputs
        box_output = output[:, :-nM*nA].view(nB, nA, -1, nPixels)
        mask_output = output[:, -nM*nA:].view(nB, nA, nM, nPixels).transpose(2, 3)

        # Get x,y,w,h,conf,cls
        coord = torch.empty_like(box_output[:, :, :4])
        coord[:, :, :2] = box_output[:, :, :2].sigmoid()    # x, y
        coord[:, :, 2:] = box_output[:, :, 2:4]             # w, h
        conf = box_output[:, :, 4].sigmoid()
        if nC > 1:
            cls = box_output[:, :, 5:].reshape(nB*nA, nC, nPixels).transpose(1, 2).reshape(-1, nC)

        with torch.no_grad():
            # Create prediction boxes
            pred_boxes = torch.FloatTensor(nB*nA*nPixels, 4)

            lin_y, lin_x = torch.meshgrid(torch.arange(nH), torch.arange(nW), **meshgrid_kw)
            lin_x = lin_x.reshape(-1).to(device)
            lin_y = lin_y.reshape(-1).to(device)
            anchor_wh = self.anchors.reshape(nA, 2, 1).to(device)

            # Compute max possible width/height network output, before the computed width/height would reach inf
            max_value = torch.tensor(1e35, dtype=pred_boxes.dtype, device=pred_boxes.device)
            max_value = (max_value / anchor_wh.max()).log().floor()

            # Get prediction coordinates
            pred_boxes[:, 0] = (coord[:, :, 0].detach() + lin_x).view(-1)
            pred_boxes[:, 1] = (coord[:, :, 1].detach() + lin_y).view(-1)
            pred_boxes[:, 2:4] = (coord[:, :, 2:4].detach().clamp(max=max_value).exp() * anchor_wh).view(-1, 2)
            pred_boxes = pred_boxes.cpu()

            # Get target values
            match_mask, idx_mask, coord_mask, conf_mask, cls_mask, tcoord, tconf, tcls = self.build_targets(pred_boxes, target, nB, nH, nW, mH, mW)
            match_mask = match_mask.to(device)
            idx_mask = idx_mask.to(device)
            coord_mask = coord_mask.expand_as(tcoord).to(device).sqrt()
            conf_mask = conf_mask.to(device).sqrt()
            tcoord = tcoord.to(device)
            tconf = tconf.to(device)
            if nC > 1:
                tcls = tcls[cls_mask].view(-1).long().to(device)
                cls_mask = cls_mask.view(-1, 1).repeat(1, nC).to(device)
                cls = cls[cls_mask].view(-1, nC)

        # Confidence loss
        if self.object_scale == 0 and self.noobject_scale == 0:
            self.loss_conf = torch.tensor(0.0, device=device)
        else:
            self.loss_conf = torch.nn.functional.mse_loss(conf*conf_mask, tconf*conf_mask, reduction='none')
            self.loss_conf = self.loss_conf.sum(dim=tuple(range(1, self.loss_conf.ndim))) / 2

        # Coordinate loss
        if self.coord_scale == 0:
            self.loss_coord = torch.tensor(0.0, device=device)
        else:
            self.loss_coord = torch.nn.functional.mse_loss(coord*coord_mask, tcoord*coord_mask, reduction='none')
            self.loss_coord = self.coord_scale * self.loss_coord.sum(dim=tuple(range(1, self.loss_coord.ndim))) / 2

        # Mask loss
        if self.mask_scale == 0 or target.shape[0] == 0:
            self.loss_mask = torch.tensor([0.0] * nB, device=device)
        else:
            self.loss_mask = self.mask_scale * self.mask_loss(proto_masks, mask_output, target, match_mask, idx_mask, nB, nH, nW, device)

        # Class loss
        if self.class_scale == 0 or nC == 1 or tcls.numel() == 0:
            self.loss_class = torch.tensor(0.0, device=device)
        else:
            self.loss_class = torch.nn.functional.cross_entropy(cls, tcls, reduction='none')
            self.loss_class = self.class_scale * self.loss_class.sum(dim=tuple(range(1, self.loss_class.ndim)))

        self.loss_total = self.loss_conf + self.loss_coord + self.loss_mask + self.loss_class
        return self.loss_total

    def build_targets(self, pred_boxes, ground_truth, nB, nH, nW, mH, mW):
        """ Compare prediction boxes and ground truths, convert ground truths to network output tensors """
        # Parameters
        nA = self.num_anchors
        nAnchors = nA*nH*nW
        nPixels = nH*nW

        # Tensors
        match_mask = torch.zeros(nB, nA, nH, nW)                        # 1 == pos ; 0 == background ; -1 == neutral / ignored
        idx_mask = torch.full((nB, nA, nH, nW), -1, dtype=torch.long)
        coord_mask = torch.zeros(nB, nA, nH, nW)
        conf_mask = torch.ones(nB, nA, nH, nW) * self.noobject_scale
        cls_mask = torch.zeros(nB, nA, nH, nW, dtype=torch.bool)
        tcoord = torch.zeros(nB, nA, 4, nH, nW)
        tconf = torch.zeros(nB, nA, nH, nW)
        tcls = torch.zeros(nB, nA, nH, nW)

        if self.training and self.seen < self.coord_prefill and self.coord_scale != 0:
            coord_mask.fill_(.01 / self.coord_scale)
            tcoord[:, :, 0].fill_(0.5)
            tcoord[:, :, 1].fill_(0.5)

        # Loop over GT
        for b, gt_filtered in ground_truth.groupby('batch_number', sort=False):
            cur_pred_boxes = pred_boxes[b*nAnchors:(b+1)*nAnchors]

            # Create ground_truth tensor
            gt = torch.from_numpy(
                gt_filtered[['x_top_left', 'y_top_left', 'width', 'height']].to_numpy(copy=True),
            ).float()

            # Convert from topleft -> center
            gt[:, 0] += gt[:, 2] / 2
            gt[:, 1] += gt[:, 3] / 2

            # Divide coordinates by stride
            gt /= self.network_stride

            # Set confidence and match mask of matching detections (neutral)
            iou_gt_pred = iou_cwh(gt, cur_pred_boxes)
            mask = (iou_gt_pred > self.iou_thresh).sum(0) >= 1
            conf_mask[b][mask.view_as(conf_mask[b])] = 0
            match_mask[b][mask.view_as(match_mask[b])] = -1

            # Find best anchor for each gt
            iou_gt_anchors = iou_wh(gt[:, 2:], self.anchors)
            _, best_anchors = iou_gt_anchors.max(1)

            # Set masks and target values for each gt
            nGT = gt.shape[0]
            gi = gt[:, 0].clamp(0, nW-1).long()
            gj = gt[:, 1].clamp(0, nH-1).long()

            match_mask[b, best_anchors, gj, gi] = 1
            idx_mask[b, best_anchors, gj, gi] = torch.arange(len(gt))
            conf_mask[b, best_anchors, gj, gi] = self.object_scale
            tconf[b, best_anchors, gj, gi] = iou_gt_pred.view(nGT, nA, nH, nW)[torch.arange(nGT), best_anchors, gj, gi]
            coord_mask[b, best_anchors, gj, gi] = 2 - torch.clamp(gt[:, 2] * gt[:, 3] / nPixels, max=1.5)
            tcoord[b, best_anchors, 0, gj, gi] = gt[:, 0] - gi.float()
            tcoord[b, best_anchors, 1, gj, gi] = gt[:, 1] - gj.float()
            tcoord[b, best_anchors, 2:4, gj, gi] = (gt[:, 2:4] / self.anchors[best_anchors, 0:2]).log()
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
                match_mask[b, best_anchors, gj, gi] = -1

        return (
            match_mask.view(nB, nA, nPixels),
            idx_mask.view(nB, nA, nPixels),
            coord_mask.view(nB, nA, 1, nPixels),
            conf_mask.view(nB, nA, nPixels),
            cls_mask.view(nB, nA, nPixels),
            tcoord.view(nB, nA, 4, nPixels),
            tconf.view(nB, nA, nPixels),
            tcls.view(nB, nA, nPixels),
        )

    def mask_loss(self, proto, mask_coef, ground_truth, match_mask, idx_mask, nB, nH, nW, device):
        nM, mH, mW = proto.shape[1:]
        proto = proto.reshape(nB, nM, -1)

        # Get batch numbers
        batch_num = torch.from_numpy(bb.util.np_col(ground_truth, 'batch_number')).to(device=device)

        # Get target masks
        if str(ground_truth.dtypes['segmentation']) == 'geos':
            gt_mask = torch.from_numpy(np.stack(bb.util.get_rasterized(ground_truth, (mH, mW), rescale=mH/nH/self.network_stride))).to(dtype=torch.bool, device=device)
        else:
            gt_mask = torch.from_numpy(np.stack(ground_truth['segmentation'].tolist())).to(dtype=torch.bool, device=device)
            if (gt_mask.shape[-2] != mH) or (gt_mask.shape[-1] != mW):
                gt_mask = torch.nn.functional.interpolate(gt_mask.float().unsqueeze(0), (mH, mW), mode='bilinear', align_corners=False).squeeze(0).gt(0.5)

        # Get relative target coordinates
        tcoord = torch.from_numpy(ground_truth[['x_top_left', 'y_top_left', 'width', 'height']].to_numpy(copy=True)).to(dtype=torch.float, device=device)
        tcoord /= self.network_stride * torch.tensor((nW, nH, nW, nH), device=device)

        # Select which masks to train on
        pos_mask = match_mask > 0
        num_pos = pos_mask.sum()
        if num_pos > self.max_masks:
            unselect = torch.randperm(num_pos)[self.max_masks:]
            positions = tuple(p[unselect] for p in pos_mask.nonzero(as_tuple=True))
            pos_mask[positions] = False

        # Get masks
        mask_loss = torch.tensor([0.0] * nB, device=device)
        for idx in range(nB):
            batch_pos = pos_mask[idx]                                           # [nA,nPixels]
            batch_idx = idx_mask[idx]                                           # [nA,nPixels]
            batch_mask = batch_num == idx
            num_pos = batch_pos.sum()
            if num_pos == 0:
                continue

            tmask = gt_mask[batch_mask][batch_idx[batch_pos]].float()           # [num_pos, mH, mW]
            tmask_coord = tcoord[batch_mask][batch_idx[batch_pos]]              # [num_pos, 4]

            # Compute masks
            batch_proto = proto[idx]
            batch_coef = mask_coef[idx, batch_pos]                              # [num_pos, nM]
            mask = (batch_coef @ batch_proto).reshape(-1, mH, mW).sigmoid()     # [num_pos, mH, mW]

            # Crop mask
            if self.training and self.seen < self.coord_prefill:
                SCALE_UP = 1.5
                tmask_coord[:, 0:2] -= tmask_coord[:, 2:4] * (SCALE_UP - 1) / 2
                tmask_coord[:, 2:4] *= SCALE_UP
            mask = crop_mask(mask, tlwh_xyxy(tmask_coord), True)

            # Compute mask loss per object
            loss = torch.nn.functional.binary_cross_entropy(mask, tmask, reduction='none')
            loss = torch.sum(loss, dim=(1, 2))

            # Rescale masks with regards to (relative coordinates)
            rescale = 1 - self.mask_rescale + 100 * self.mask_rescale * tmask_coord[:, 2] * tmask_coord[:, 3]
            loss /= rescale

            # Append mask loss per batch
            mask_loss[idx] = loss.mean()

        return mask_loss


class MultiScaleMaskedRegionLoss(MultiScale, MaskedRegionLoss):
    """ Computes the region loss for multiscale anchor detection networks. |br|
    This class is is meant to be used on the output of multiple :class:`~lightnet.network.head.DetectionAnchor` modules,
    together with a brambox dataframe of target annotations.

    Args:
        num_classes (int): number of classes to detect
        anchors (ln.util.Anchors): multi-scale list of anchor boxes
        network_stride (list): Downsampling factors of the network (most lightnet networks have a `stride` attribute)
        seen (optional, torch.Tensor): How many images the network has already been trained on; Default **0**
        coord_scale (optional, float): weight of bounding box coordinates; Default **1.0**
        noobject_scale (optional, float): weight of regions without target boxes; Default **1.0**
        object_scale (optional, float): weight of regions with target boxes; Default **5.0**
        class_scale (optional, float): weight of categorical predictions; Default **1.0**
        iou_thresh (optional, float): minimum iou between a predicted box and ground truth for them to be considered matching; Default **0.6**
        coord_prefill (optional, int): This parameter controls for how many training samples the network will prefill the target coordinates, biassing the network to predict the center at **.5,.5**; Default **12800**

    Note:
        All parameters are the same as :class:`~lightnet.network.loss.MaskedRegionLoss`, except for `anchors` and `stride`. |br|
        These 2 parameters need separate values for each different network output scale and thus need to be lists of the original parameter.
    """
    LOSS = MaskedRegionLoss
    MULTISCALE_ARGS = ('anchors', 'network_stride')
    MULTI_OUTPUT = True

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

    def _setup_forward_kwargs(self, output, target, kwargs):
        if 'seen' not in kwargs:
            kwargs['seen'] = self.seen.item() + output[0][0].shape[0]
        return kwargs
