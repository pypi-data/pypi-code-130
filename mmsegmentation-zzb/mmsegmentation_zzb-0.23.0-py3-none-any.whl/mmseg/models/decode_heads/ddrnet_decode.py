import torch
import torch.nn as nn
from mmcv.cnn import ConvModule

from ..builder import HEADS
from .decode_head import BaseDecodeHead


@HEADS.register_module()
class DdrNetHead(BaseDecodeHead):
    def __init__(self,**kwargs):
        super(DdrNetHead, self).__init__(**kwargs)

    def forward(self, inputs):
        return self.cls_seg(inputs)
