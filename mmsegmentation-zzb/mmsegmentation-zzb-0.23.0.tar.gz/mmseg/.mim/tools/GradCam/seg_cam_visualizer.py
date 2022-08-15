# Copyright (c) OpenMMLab. All rights reserved.
import bisect
import copy

import cv2
import mmcv
import numpy as np
import torch
import torch.nn as nn
import torchvision
from mmcv.ops import RoIPool
from mmcv.parallel import collate, scatter
from mmcv.runner import load_checkpoint
from mmseg.core import get_classes
from mmseg.datasets import replace_ImageToTensor
from mmseg.datasets.pipelines import Compose
from mmseg.models import build_segmentor
try:
    from pytorch_grad_cam import (AblationCAM, AblationLayer,
                                  ActivationsAndGradients)
    from pytorch_grad_cam.base_cam import BaseCAM
    from pytorch_grad_cam.utils.image import scale_cam_image, show_cam_on_image
    from pytorch_grad_cam.utils.svd_on_activations import get_2d_projection
except ImportError:
    raise ImportError('Please run `pip install "grad-cam"` to install '
                      '3rd party package pytorch_grad_cam.')


class SegCAMModel(nn.Module):
    def __init__(self, cfg, checkpoin, device='cuda:0'):
        super(SegCAMModel, self).__init__()
        self.cfg = cfg
        self.device = device
        self.checkpoin = checkpoin
        self.segmentor = self.build_segmentor()

        self.return_loss = False
        self.input_data == None
        self.img = None

    def build_segmentor(self):
        cfg = copy.deepcopy(self.cfg)

        segmentor = build_segmentor(cfg.model, train_cfg=cfg.get('train_cfg'), test_cfg=cfg.get('test.cfg'))
        if self.checkpoint is not None:
            checkpoint = load_checkpoint(
                segmentor, self.checkpoint, map_location='cpu')
            if 'CLASSES' in checkpoint.get('meta', {}):
                segmentor.CLASSES = checkpoint['meta']['CLASSES']
                segmentor.PALETTE = checkpoint['meta']['PALETTE']
            else:
                import warnings
                warnings.simplefilter('once')
                warnings.warn('Class names are not saved in the checkpoint\'s '
                              'meta data, use COCO classes by default.')
                segmentor.CLASSES = get_classes('coco')

        segmentor.to(self.device)
        segmentor.eval()
        return segmentor

    def set_return_loss(self, return_loss):
        self.return_loss = return_loss

    def set_input_data(self, img, labels=None):
        self.img = img
        cfg = copy.deepcopy(self.cfg)
        if self.return_loss:
            assert labels is not None
            cfg.data.test.pipeline[0].type = 'LoadImageFromWebcam'
            cfg.data.test.pipeline = replace_ImageToTensor(
                cfg.data.test.pipeline)
            cfg.data.test.pipeline[1].transforms[-1] = dict(
                type='Collect', keys=['img', 'gt_semantic_seg'])
            test_pipeline = Compose(cfg.data.test.pipeline)
            # TODO: suport mask
            data = dict(
                img=self.img,
                gt_semantic_seg=labels.astype(np.long)
            )
            data = test_pipeline(data)
            data = collate([data], samples_per_gpu=1)
            # just get the actual data from DataContainer
            data['img_metas'] = [
                img_metas.data[0][0] for img_metas in data['img_metas']
            ]
            data['img'] = [img.data[0] for img in data['img']]
            data['gt_semantic_seg'] = [
                gt_semantic_seg.data[0] for gt_semantic_seg in data['gt_semantic_seg']
            ]
            if next(self.segmentor.parameters()).is_cuda:
                # scatter to specified GPU
                data = scatter(data, [self.device])[0]
                data['img'] = data['img'][0]
                data['gt_semantic_seg'] = data['gt_semantic_seg'][0]
        else:
            # set loading pipeline type
            cfg.data.test.pipeline[0].type = 'LoadImageFromWebcam'
            data = dict(img=self.img)
            cfg.data.test.pipeline = replace_ImageToTensor(
                cfg.data.test.pipeline)
            test_pipeline = Compose(cfg.data.test.pipeline)
            data = test_pipeline(data)
            data = collate([data], samples_per_gpu=1)
            # just get the actual data from DataContainer
            data['img_metas'] = [
                img_metas.data[0] for img_metas in data['img_metas']
            ]
            data['img'] = [img.data[0] for img in data['img']]

            if next(self.detector.parameters()).is_cuda:
                # scatter to specified GPU
                data = scatter(data, [self.device])[0]
            else:
                for m in self.detector.modules():
                    assert not isinstance(
                        m, RoIPool
                    ), 'CPU inference with RoIPool is not supported currently.'

        self.input_data = data

    def __call__(self, *args, **kwargs):
        assert self.input_data is not None
        if self.return_loss:
            loss = self.segmentor(return_loss=True, **self.input_data)
        else:
            with torch.no_grad():
                results = self.segmentor(return_loss=False, rescale=True, **self.input_data)[0]
                return results


class SegCAMVisualizer:
    """mmseg cam visualization class.

        Args:
            method:  CAM method. Currently supports
               `ablationcam`,`eigencam` and `featmapam`.
            model (nn.Module): MMDet model.
            target_layers (list[torch.nn.Module]): The target layers
                you want to visualize.
            reshape_transform (Callable, optional): Function of Reshape
                and aggregate feature maps. Defaults to None.
        """
    def __init__(self,
                 method_class,
                 model,
                 target_layers,
                 reshape_transform=None,
                 is_need_grad=False,
                 extra_params=None):
        self.target_layers = target_layers
        self.reshape_transform = reshape_transform
        self.is_need_grad = is_need_grad
        if method_class.__name__ == 'AblationCAM':
            batch_size = extra_params.get('batch_size', 1)
            ratio_channels_to_ablate = extra_params.get(
                'ratio_channels_to_ablate', 1.)
            self.cam = AblationCAM(
                model,
                target_layers,
                use_cuda=True if 'cuda' in model.device else False,
                reshape_transform=reshape_transform,
                batch_size=batch_size,
                ablation_layer=extra_params['ablation_layer'],
                ratio_channels_to_ablate=ratio_channels_to_ablate)
        else:
            self.cam = method_class(
                model,
                target_layers,
                use_cuda=True if 'cuda' in model.device else False,
                reshape_transform=reshape_transform,
            )
            if self.is_need_grad:
                self.cam.activations_and_grads.release()
        self.classes = model.detector.CLASSES
        self.COLORS = np.random.uniform(0, 255, size=(len(self.classes), 3))

    def switch_activations_and_grads(self, model):
        self.cam.model = model

        if self.is_need_grad is True:
            self.cam.activations_and_grads = ActivationsAndGradients(
                model, self.target_layers, self.reshape_transform)
            self.is_need_grad = False
        else:
            self.cam.activations_and_grads.release()
            self.is_need_grad = True

    def __call__(self, img, targets, aug_smooth=False, eigen_smooth=False):
        img = torch.from_numpy(img)[None].permute(0, 3, 1, 2)
        return self.cam(img, targets, aug_smooth, eigen_smooth)[0, :]