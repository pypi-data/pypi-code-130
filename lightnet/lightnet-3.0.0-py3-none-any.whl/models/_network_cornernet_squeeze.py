#
#   Cornernet Squeeze model
#   Copyright EAVISE
#
import logging
import re
import torch.nn as nn
import lightnet.network as lnn

__all__ = ['CornernetSqueeze']
log = logging.getLogger('lightnet.models')


class CornernetSqueeze(lnn.module.Lightnet):
    """ Cornernet Squeeze implementation :cite:`cornernet_lite`.

    .. admonition:: Experimental

       This network implementation is still in development
       and might not be yielding the same results as the official implementation.
       Use at your own risk!

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**
        inference_only (boolean, optional): Whether to load the model purely for inference; Default **False**

    Attributes:
        self.stride: Subsampling factor of the network (input_dim / output_dim)
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_princeton_vl: Remapping rules for weights from the `official CornerNet implementation <cornernetImpl_>`_.
        self.remap_v1: Remapping rules for weights from yolt models before lightnet v3.0.0

    .. _cornernetImpl: https://github.com/princeton-vl/CornerNet-Lite
    """
    stride = 8
    inner_stride = 128

    MODEL_VERSION = 1
    remap_v1 = [
        (r'^extractor\.(.*)', r'backbone.module.\1'),
        (r'^detector.(.*?).13_(.*)', r'head.\1.1_\2'),
        (r'^detector.(.*?).14_(.*)', r'head.\1.2_\2'),
        (r'^detector.(.*?).15_(.*)', r'head.\1.3_\2'),
        (r'^detector.(.*?).17_(.*)', r'head.\1.5_\2'),
        (r'^detector.(.*?).18_(.*)', r'head.\1.6_\2'),
        (r'^detector.(.*?).20_(.*)', r'head.\1.8_\2'),
        (r'^detector.(.*?).21_(.*)', r'head.\1.9_\2'),
        (r'^detector.(.*?).23_(.*)', r'head.\1.11_\2'),
        (r'^detector.(.*?).24_(.*)', r'head.\1.1_\2'),
        (r'^detector.(.*?).25_(.*)', r'head.\1.2_\2'),
        (r'^detector.(.*?).26_(.*)', r'head.\1.3_\2'),
        (r'^detector.(.*?).28_(.*)', r'head.\1.5_\2'),
        (r'^detector.(.*?).29_(.*)', r'head.\1.6_\2'),
        (r'^detector.(.*?).31_(.*)', r'head.\1.8_\2'),
        (r'^detector.(.*?).32_(.*)', r'head.\1.9_\2'),
        (r'^detector.(.*?).34_(.*)', r'head.\1.11_\2'),
        (r'^intermediate.(.*?).35_(.*)', r'inter_head.\1.1_\2'),
        (r'^intermediate.(.*?).36_(.*)', r'inter_head.\1.2_\2'),
        (r'^intermediate.(.*?).37_(.*)', r'inter_head.\1.3_\2'),
        (r'^intermediate.(.*?).39_(.*)', r'inter_head.\1.5_\2'),
        (r'^intermediate.(.*?).40_(.*)', r'inter_head.\1.6_\2'),
        (r'^intermediate.(.*?).42_(.*)', r'inter_head.\1.8_\2'),
        (r'^intermediate.(.*?).43_(.*)', r'inter_head.\1.9_\2'),
        (r'^intermediate.(.*?).45_(.*)', r'inter_head.\1.11_\2'),
        (r'^intermediate.(.*?).46_(.*)', r'inter_head.\1.1_\2'),
        (r'^intermediate.(.*?).47_(.*)', r'inter_head.\1.2_\2'),
        (r'^intermediate.(.*?).48_(.*)', r'inter_head.\1.3_\2'),
        (r'^intermediate.(.*?).50_(.*)', r'inter_head.\1.5_\2'),
        (r'^intermediate.(.*?).51_(.*)', r'inter_head.\1.6_\2'),
        (r'^intermediate.(.*?).53_(.*)', r'inter_head.\1.8_\2'),
        (r'^intermediate.(.*?).54_(.*)', r'inter_head.\1.9_\2'),
        (r'^intermediate.(.*?).56_(.*)', r'inter_head.\1.11_\2'),
    ]

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
        inference_only=False,
    ):
        log.experimental('CornernetSqueeze is still in development. Use at your own risk!')

        self.num_classes = num_classes
        self.input_channels = input_channels
        self.inference_only = inference_only

        # Network
        self.backbone = lnn.layer.FeatureExtractor(
            lnn.backbone.Cornernet.Squeeze(input_channels, 256),
            ['residual.5_convbatch'],
            True,
        )

        self.head = lnn.head.DetectionCorner(256, num_classes, squeeze=True)
        if not self.inference_only:
            self.inter_head = lnn.head.DetectionCorner(256, num_classes, squeeze=True)

        # Set mode
        if self.inference_only:
            self.eval()

    def __init_weights__(self, name, mod):
        if name.endswith('output.heatmap.4_conv'):
            nn.init.kaiming_normal_(mod.weight, mode='fan_out', nonlinearity='relu')
            nn.init.constant_(mod.bias, -2.19)
            return True

        return super().__init_weights__(name, mod)

    def forward(self, x):
        x, feat_5 = self.backbone(x)
        out1 = self.head(x)

        if self.training:
            out2 = self.inter_head(feat_5)
            return (out1, out2)
        else:
            return out1

    def train(self, mode=True):
        if mode and self.inference_only:
            raise ValueError('Cannot set training mode for inference_only model')
        return super().train(mode)

    @staticmethod
    def remap_princeton_vl(k):
        # HOURGLASSES
        if k.startswith('module.hg.hgs'):
            if k[14] == '0':
                nk = 'backbone.module.residual.4_hourglass.layers.'
            else:
                nk = 'backbone.module.8_hourglass.layers.'

            k = (
                k[16:]
                .replace('up1', 'upper')
                .replace('up2', 'down.down2.2')
                .replace('low1', 'down.down1')
                .replace('low3', 'down.down2')
                .replace('conv1', '0')
                .replace('bn1', '1')
                .replace('conv_1x1', '2.0')
                .replace('conv_3x3', '2.1')
                .replace('bn2', '3')
            )
            k = re.sub(r'low2.(\d+)', r'down.inner.\1', k)
            k = k.replace('low2', 'down.inner.layers')
            k = k.replace('skip', 'skip.layers')

            return nk+k

        # HEAD
        if k.startswith('module.tl') or k.startswith('module.br'):
            _, mod, num, _ = k.split('.', 3)
            corner, mod = mod.split('_')

            if num == '0':
                nk = 'inter_head.'
            else:
                nk = 'head.'
            if corner == 'tl':
                nk += 'topleft.'
            else:
                nk += 'bottomright.'

            if mod == 'modules':
                return (
                    (r'p1_conv1.conv.(.*)$',    nk + r'1_corner.layers.pool.0.0.layers.0.\1'),
                    (r'p1_conv1.bn.(.*)$',      nk + r'1_corner.layers.pool.0.0.layers.1.\1'),
                    (r'p2_conv1.conv.(.*)$',    nk + r'1_corner.layers.pool.1.0.layers.0.\1'),
                    (r'p2_conv1.bn.(.*)$',      nk + r'1_corner.layers.pool.1.0.layers.1.\1'),
                    (r'p_conv1.(.*)$',          nk + r'1_corner.layers.pool.post.layers.0.\1'),
                    (r'p_bn1.(.*)$',            nk + r'1_corner.layers.pool.post.layers.1.\1'),
                    (r'conv1.(.*)$',            nk + r'1_corner.layers.conv.layers.0.\1'),
                    (r'bn1.(.*)$',              nk + r'1_corner.layers.conv.layers.1.\1'),
                    (r'conv2.conv.(.*)$',       nk + r'2_convbatch.layers.0.\1'),
                    (r'conv2.bn.(.*)$',         nk + r'2_convbatch.layers.1.\1'),
                )
            if mod == 'heats':
                return (
                    (r'0.conv.(.*)$',           nk + r'output.heatmap.3_conv.layers.0.\1'),
                    (r'[01].1.(.*)$',           nk + r'output.heatmap.4_conv.\1'),
                )
            if mod == 'tags':
                return (
                    (r'0.conv.(.*)$',           nk + r'output.embedding.5_conv.layers.0.\1'),
                    (r'[01].1.(.*)$',           nk + r'output.embedding.6_conv.\1'),
                )
            if mod == 'offs':
                return (
                    (r'0.conv.(.*)$',           nk + r'output.offset.7_conv.layers.0.\1'),
                    (r'[01].1.(.*)$',           nk + r'output.offset.8_conv.\1'),
                )

        # REST OF BACKBONE
        return (
            (r'^module.hg.pre.0.conv.(.*)',     r'backbone.module.1_convbatch.layers.0.\1'),
            (r'^module.hg.pre.0.bn.(.*)',       r'backbone.module.1_convbatch.layers.1.\1'),
            (r'^module.hg.pre.1.conv1.(.*)',    r'backbone.module.2_residual.0.\1'),
            (r'^module.hg.pre.1.bn1.(.*)',      r'backbone.module.2_residual.1.\1'),
            (r'^module.hg.pre.1.conv2.(.*)',    r'backbone.module.2_residual.3.\1'),
            (r'^module.hg.pre.1.bn2.(.*)',      r'backbone.module.2_residual.4.\1'),
            (r'^module.hg.pre.1.skip.(.*)',     r'backbone.module.2_residual.skip.layers.\1'),
            (r'^module.hg.pre.2.conv1.(.*)',    r'backbone.module.3_residual.0.\1'),
            (r'^module.hg.pre.2.bn1.(.*)',      r'backbone.module.3_residual.1.\1'),
            (r'^module.hg.pre.2.conv2.(.*)',    r'backbone.module.3_residual.3.\1'),
            (r'^module.hg.pre.2.bn2.(.*)',      r'backbone.module.3_residual.4.\1'),
            (r'^module.hg.pre.2.skip.(.*)',     r'backbone.module.3_residual.skip.layers.\1'),
            (r'^module.hg.cnvs.0.conv.(.*)',    r'backbone.module.residual.5_convbatch.layers.0.\1'),
            (r'^module.hg.cnvs.0.bn.(.*)',      r'backbone.module.residual.5_convbatch.layers.1.\1'),
            (r'^module.hg.cnvs.1.conv.(.*)',    r'backbone.module.9_convbatch.layers.0.\1'),
            (r'^module.hg.cnvs.1.bn.(.*)',      r'backbone.module.9_convbatch.layers.1.\1'),
            (r'^module.hg.cnvs_.0.0.(.*)',      r'backbone.module.residual.6_convbatch.layers.0.\1'),
            (r'^module.hg.cnvs_.0.1.(.*)',      r'backbone.module.residual.6_convbatch.layers.1.\1'),
            (r'^module.hg.inters.0.conv1.(.*)', r'backbone.module.7_residual.0.\1'),
            (r'^module.hg.inters.0.bn1.(.*)',   r'backbone.module.7_residual.1.\1'),
            (r'^module.hg.inters.0.conv2.(.*)', r'backbone.module.7_residual.3.\1'),
            (r'^module.hg.inters.0.bn2.(.*)',   r'backbone.module.7_residual.4.\1'),
            (r'^module.hg.inters.0.skip.(.*)',  r'backbone.module.7_residual.skip.layers.\1'),
            (r'^module.hg.inters_.0.0.(.*)',    r'backbone.module.residual.skip.layers.0.\1'),
            (r'^module.hg.inters_.0.1.(.*)',    r'backbone.module.residual.skip.layers.1.\1'),
        )

    @staticmethod
    def remap_v1(k):
        if k.startswith('extractor'):
            _, remainder = k.split('.', 1)

            if 'skip' in remainder:
                remainder = remainder.replace('skip', 'skip.layers')
            if 'para' in remainder:
                remainder = remainder.replace('para.0', 'residual')
                remainder = remainder.replace('para.1', 'residual.skip')

            if '6_conv' in remainder:
                pre, post = remainder.split('.6_conv.')
                return f'backbone.module.{pre}.6_convbatch.layers.0.{post}'
            if '7_batchnorm' in remainder:
                pre, post = remainder.split('.7_batchnorm.')
                return f'backbone.module.{pre}.6_convbatch.layers.1.{post}'
            if '8_conv' in remainder:
                pre, post = remainder.split('.8_conv.')
                return f'backbone.module.{pre}.layers.0.{post}'
            if '9_batchnorm' in remainder:
                pre, post = remainder.split('.9_batchnorm.')
                return f'backbone.module.{pre}.layers.1.{post}'
            if '10_residual' in remainder:
                return f'backbone.module.7{remainder[2:]}'
            if '11_hourglass' in remainder:
                return f'backbone.module.8{remainder[2:]}'
            if '12_convbatch' in remainder:
                return f'backbone.module.9{remainder[2:]}'

            return f'backbone.module.{remainder}'
        else:
            return (
                (r'^detector.(.*?).13_corner.layers.pool.post.(.*)',    r'head.\1.1_corner.layers.pool.post.layers.\2'),
                (r'^detector.(.*?).13_corner.layers.conv.(.*)',         r'head.\1.1_corner.layers.conv.layers.\2'),
                (r'^detector.(.*?).13_(.*)',                            r'head.\1.1_\2'),
                (r'^detector.(.*?).14_(.*)',                            r'head.\1.2_\2'),
                (r'^detector.(.*?).15_(\w+).(.*)',                      r'head.\1.3_\2.layers.0.\3'),
                (r'^detector.(.*?).17_(.*)',                            r'head.\1.4_\2'),
                (r'^detector.(.*?).18_(\w+).(.*)',                      r'head.\1.5_\2.layers.0.\3'),
                (r'^detector.(.*?).20_(.*)',                            r'head.\1.6_\2'),
                (r'^detector.(.*?).21_(\w+).(.*)',                      r'head.\1.7_\2.layers.0.\3'),
                (r'^detector.(.*?).23_(.*)',                            r'head.\1.8_\2'),
                (r'^detector.(.*?).24_corner.layers.pool.post.(.*)',    r'head.\1.1_corner.layers.pool.post.layers.\2'),
                (r'^detector.(.*?).24_corner.layers.conv.(.*)',         r'head.\1.1_corner.layers.conv.layers.\2'),
                (r'^detector.(.*?).24_(.*)',                            r'head.\1.1_\2'),
                (r'^detector.(.*?).25_(.*)',                            r'head.\1.2_\2'),
                (r'^detector.(.*?).26_(\w+).(.*)',                      r'head.\1.3_\2.layers.0.\3'),
                (r'^detector.(.*?).28_(.*)',                            r'head.\1.4_\2'),
                (r'^detector.(.*?).29_(\w+).(.*)',                      r'head.\1.5_\2.layers.0.\3'),
                (r'^detector.(.*?).31_(.*)',                            r'head.\1.6_\2'),
                (r'^detector.(.*?).32_(\w+).(.*)',                      r'head.\1.7_\2.layers.0.\3'),
                (r'^detector.(.*?).34_(.*)',                            r'head.\1.8_\2'),
                (r'^intermediate.(.*?).35_corner.layers.pool.post.(.*)',    r'inter_head.\1.1_corner.layers.pool.post.layers.\2'),
                (r'^intermediate.(.*?).35_corner.layers.conv.(.*)',         r'inter_head.\1.1_corner.layers.conv.layers.\2'),
                (r'^intermediate.(.*?).35_(.*)',                            r'inter_head.\1.1_\2'),
                (r'^intermediate.(.*?).36_(.*)',                            r'inter_head.\1.2_\2'),
                (r'^intermediate.(.*?).37_(\w+).(.*)',                      r'inter_head.\1.3_\2.layers.0.\3'),
                (r'^intermediate.(.*?).39_(.*)',                            r'inter_head.\1.4_\2'),
                (r'^intermediate.(.*?).40_(\w+).(.*)',                      r'inter_head.\1.5_\2.layers.0.\3'),
                (r'^intermediate.(.*?).42_(.*)',                            r'inter_head.\1.6_\2'),
                (r'^intermediate.(.*?).43_(\w+).(.*)',                      r'inter_head.\1.7_\2.layers.0.\3'),
                (r'^intermediate.(.*?).45_(.*)',                            r'inter_head.\1.8_\2'),
                (r'^intermediate.(.*?).46_corner.layers.pool.post.(.*)',    r'inter_head.\1.1_corner.layers.pool.post.layers.\2'),
                (r'^intermediate.(.*?).46_corner.layers.conv.(.*)',         r'inter_head.\1.1_corner.layers.conv.layers.\2'),
                (r'^intermediate.(.*?).46_(.*)',                            r'inter_head.\1.1_\2'),
                (r'^intermediate.(.*?).47_(.*)',                            r'inter_head.\1.2_\2'),
                (r'^intermediate.(.*?).48_(\w+).(.*)',                      r'inter_head.\1.3_\2.layers.0.\3'),
                (r'^intermediate.(.*?).50_(.*)',                            r'inter_head.\1.4_\2'),
                (r'^intermediate.(.*?).51_(\w+).(.*)',                      r'inter_head.\1.5_\2.layers.0.\3'),
                (r'^intermediate.(.*?).53_(.*)',                            r'inter_head.\1.6_\2'),
                (r'^intermediate.(.*?).54_(\w+).(.*)',                      r'inter_head.\1.7_\2.layers.0.\3'),
                (r'^intermediate.(.*?).56_(.*)',                            r'inter_head.\1.8_\2'),
            )
