# Copyright (c) OpenMMLab. All rights reserved.
import argparse
import os.path
from functools import partial

import cv2
import mmcv
import numpy as np
from mmcv import Config, DictAction

from mmseg.utils.det_cam_visualizer import (DetAblationLayer,
                                            DetBoxScoreTarget, DetCAMModel,
                                            DetCAMVisualizer, EigenCAM,
                                            FeatmapAM, reshape_transform)
from tools.GradCam.seg_cam_visualizer import SegCAMModel
try:
    from pytorch_grad_cam import (AblationCAM, EigenGradCAM, GradCAM,
                                  GradCAMPlusPlus, LayerCAM, XGradCAM)
except ImportError:
    raise ImportError('Please run `pip install "grad-cam"` to install '
                      '3rd party package pytorch_grad_cam.')

GRAD_FREE_METHOD_MAP = {
    'ablationcam': AblationCAM,
    'eigencam': EigenCAM,
    # 'scorecam': ScoreCAM, # consumes too much memory
    'featmapam': FeatmapAM
}

GRAD_BASE_METHOD_MAP = {
    'gradcam': GradCAM,
    'gradcam++': GradCAMPlusPlus,
    'xgradcam': XGradCAM,
    'eigengradcam': EigenGradCAM,
    'layercam': LayerCAM
}

ALL_METHODS = list(GRAD_FREE_METHOD_MAP.keys() | GRAD_BASE_METHOD_MAP.keys())

def parse_args():
    parser = argparse.ArgumentParser(description='Visualize CAM')
    parser.add_argument('--img', help='Image file',
                        default='E:/pycharmwork/canny/image/car.jpg')
    parser.add_argument('--config', help='Config file',
                        default='E:/AI/project/mmsegmentation/configs/bisenet_liteaspp_cross_cbam/bisenet_liteaspp_cross_cbam_512x512_80k_voc.py')
    parser.add_argument('--checkpoint', help='Checkpoint file',
                        default='E:/AI/project/mmsegmentation/work_dirs/bisenet_liteaspp_cross_cbam_512x512_80k_voc/iter_80000.pth')
    parser.add_argument(
        '--method',
        default='gradcam',
        help='Type of method to use, supports '
             f'{", ".join(ALL_METHODS)}.')
    parser.add_argument(
        '--target-layers',
        default=['decode_head.last_crosse_cabm'],
        nargs='+',
        type=str,
        help='The target layers to get CAM, if not set, the tool will '
             'specify the backbone.layer3')
    parser.add_argument(
        '--preview-model',
        default=False,
        action='store_true',
        help='To preview all the model layers')
    parser.add_argument(
        '--device', default='cuda:0', help='Device used for inference')
    parser.add_argument(
        '--max-shape',
        nargs='+',
        type=int,
        default=20,
        help='max shapes. Its purpose is to save GPU memory. '
             'The activation map is scaled and then evaluated. '
             'If set to -1, it means no scaling.')
    parser.add_argument(
        '--aug-smooth',
        default=False,
        action='store_true',
        help='Wether to use test time augmentation, default not to use')
    parser.add_argument(
        '--eigen-smooth',
        default=False,
        action='store_true',
        help='Reduce noise by taking the first principle componenet of '
             '``cam_weights*activations``')
    args = parser.parse_args()
    if args.method.lower() not in (GRAD_FREE_METHOD_MAP.keys()
                                   | GRAD_BASE_METHOD_MAP.keys()):
        raise ValueError(f'invalid CAM type {args.method},'
                         f' supports {", ".join(ALL_METHODS)}.')

    return args

def init_model_cam(args, cfg):
    model = SegCAMModel(cfg, args.checkpoint, device=args.device)
    target_layers = []
    for target_layer in args.target_layers:
        try:
            target_layers.append(eval(f'model.detector.{target_layer}'))
        except Exception as e:
            print(model.segmentor)
            raise RuntimeError('layer does not exist', e)

    extra_params = {
        'batch_size': args.batch_size,
        'ablation_layer': DetAblationLayer(),
        'ratio_channels_to_ablate': args.ratio_channels_to_ablate
    }
    method_class = GRAD_FREE_METHOD_MAP[args.method]
    is_need_grad = False


def main():
    args = parse_args()
    cfg = Config.fromfile(args.config)
    if args.cfg_options is not None:
        cfg.merge_from_dict(args.cfg_options)
    model, seg_cam_visualizer = init_model_cam(args, cfg)

if __name__ == 'main':
    main()