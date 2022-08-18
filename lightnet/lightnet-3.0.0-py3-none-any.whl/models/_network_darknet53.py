#
#   Darknet Darknet53 model
#   Copyright EAVISE
#
import torch.nn as nn
import lightnet.network as lnn

__all__ = ['Darknet53']


class Darknet53(lnn.module.Darknet):
    """ Darknet53 implementation :cite:`yolo_v3`.

    Args:
        num_classes (int): Number of classes
        input_channels (int, optional): Number of input channels; Default **3**

    Attributes:
        self.inner_stride: Maximal internal subsampling factor of the network (input dimension should be a multiple of this)
        self.remap_v1: Remapping rules for weights from yolt models before lightnet v3.0.0
    """
    inner_stride = 32

    MODEL_VERSION = 1
    remap_v1 = (
        (r'^layers.a_residual.3_\w+.(.*)', r'backbone.3_residual.0.\1'),
        (r'^layers.a_residual.4_\w+.(.*)', r'backbone.3_residual.1.\1'),
        (r'^layers.5_(.*)', r'backbone.4_\1'),
        (r'^layers.b_residual.6_\w+.(.*)', r'backbone.5_residual.0.\1'),
        (r'^layers.b_residual.7_\w+.(.*)', r'backbone.5_residual.1.\1'),
        (r'^layers.c_residual.8_\w+.(.*)', r'backbone.6_residual.0.\1'),
        (r'^layers.c_residual.9_\w+.(.*)', r'backbone.6_residual.1.\1'),
        (r'^layers.10_(.*)', r'backbone.7_\1'),
        (r'^layers.d_residual.11_\w+.(.*)', r'backbone.8_residual.0.\1'),
        (r'^layers.d_residual.12_\w+.(.*)', r'backbone.8_residual.1.\1'),
        (r'^layers.e_residual.13_\w+.(.*)', r'backbone.9_residual.0.\1'),
        (r'^layers.e_residual.14_\w+.(.*)', r'backbone.9_residual.1.\1'),
        (r'^layers.f_residual.15_\w+.(.*)', r'backbone.10_residual.0.\1'),
        (r'^layers.f_residual.16_\w+.(.*)', r'backbone.10_residual.1.\1'),
        (r'^layers.g_residual.17_\w+.(.*)', r'backbone.11_residual.0.\1'),
        (r'^layers.g_residual.18_\w+.(.*)', r'backbone.11_residual.1.\1'),
        (r'^layers.h_residual.19_\w+.(.*)', r'backbone.12_residual.0.\1'),
        (r'^layers.h_residual.20_\w+.(.*)', r'backbone.12_residual.1.\1'),
        (r'^layers.i_residual.21_\w+.(.*)', r'backbone.13_residual.0.\1'),
        (r'^layers.i_residual.22_\w+.(.*)', r'backbone.13_residual.1.\1'),
        (r'^layers.j_residual.23_\w+.(.*)', r'backbone.14_residual.0.\1'),
        (r'^layers.j_residual.24_\w+.(.*)', r'backbone.14_residual.1.\1'),
        (r'^layers.k_residual.25_\w+.(.*)', r'backbone.15_residual.0.\1'),
        (r'^layers.k_residual.26_\w+.(.*)', r'backbone.15_residual.1.\1'),
        (r'^layers.27_(.*)', r'backbone.16_\1'),
        (r'^layers.l_residual.28_\w+.(.*)', r'backbone.17_residual.0.\1'),
        (r'^layers.l_residual.29_\w+.(.*)', r'backbone.17_residual.1.\1'),
        (r'^layers.m_residual.30_\w+.(.*)', r'backbone.18_residual.0.\1'),
        (r'^layers.m_residual.31_\w+.(.*)', r'backbone.18_residual.1.\1'),
        (r'^layers.n_residual.32_\w+.(.*)', r'backbone.19_residual.0.\1'),
        (r'^layers.n_residual.33_\w+.(.*)', r'backbone.19_residual.1.\1'),
        (r'^layers.o_residual.34_\w+.(.*)', r'backbone.20_residual.0.\1'),
        (r'^layers.o_residual.35_\w+.(.*)', r'backbone.20_residual.1.\1'),
        (r'^layers.p_residual.36_\w+.(.*)', r'backbone.21_residual.0.\1'),
        (r'^layers.p_residual.37_\w+.(.*)', r'backbone.21_residual.1.\1'),
        (r'^layers.q_residual.38_\w+.(.*)', r'backbone.22_residual.0.\1'),
        (r'^layers.q_residual.39_\w+.(.*)', r'backbone.22_residual.1.\1'),
        (r'^layers.r_residual.40_\w+.(.*)', r'backbone.23_residual.0.\1'),
        (r'^layers.r_residual.41_\w+.(.*)', r'backbone.23_residual.1.\1'),
        (r'^layers.s_residual.42_\w+.(.*)', r'backbone.24_residual.0.\1'),
        (r'^layers.s_residual.43_\w+.(.*)', r'backbone.24_residual.1.\1'),
        (r'^layers.44_(.*)', r'backbone.25_\1'),
        (r'^layers.t_residual.45_\w+.(.*)', r'backbone.26_residual.0.\1'),
        (r'^layers.t_residual.46_\w+.(.*)', r'backbone.26_residual.1.\1'),
        (r'^layers.u_residual.47_\w+.(.*)', r'backbone.27_residual.0.\1'),
        (r'^layers.u_residual.48_\w+.(.*)', r'backbone.27_residual.1.\1'),
        (r'^layers.v_residual.49_\w+.(.*)', r'backbone.28_residual.0.\1'),
        (r'^layers.v_residual.50_\w+.(.*)', r'backbone.28_residual.1.\1'),
        (r'^layers.w_residual.51_\w+.(.*)', r'backbone.29_residual.0.\1'),
        (r'^layers.w_residual.52_\w+.(.*)', r'backbone.29_residual.1.\1'),
        (r'^layers.54_conv.(.*)', r'head.1.\1'),
        (r'^layers.(.*)', r'backbone.\1'),
    )

    def __init_module__(
        self,
        num_classes,
        input_channels=3,
    ):
        self.num_classes = num_classes

        # Network
        self.backbone = lnn.backbone.Darknet.DN_53(input_channels, 1024)
        self.head = lnn.head.ClassificationConv(1024, num_classes)

    def __init_weights__(self, name, mod):
        if isinstance(mod, nn.Conv2d):
            nn.init.kaiming_normal_(mod.weight, a=0.1, mode='fan_out')
            if mod.bias is not None:
                nn.init.constant_(mod.bias, 0)
            return True

        return super().__init_weights__(name, mod)

    def forward(self, x):
        x = self.backbone(x)
        x = self.head(x)

        return x
