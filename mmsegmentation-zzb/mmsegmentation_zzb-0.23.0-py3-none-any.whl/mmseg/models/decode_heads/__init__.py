# Copyright (c) OpenMMLab. All rights reserved.
from .ann_head import ANNHead
from .apc_head import APCHead
from .aspp_head import ASPPHead
from .cc_head import CCHead
from .da_head import DAHead
from .dm_head import DMHead
from .dnl_head import DNLHead
from .dpt_head import DPTHead
from .ema_head import EMAHead
from .enc_head import EncHead
from .fcn_head import FCNHead
from .fpn_head import FPNHead
from .gc_head import GCHead
from .isa_head import ISAHead
from .knet_head import IterativeDecodeHead, KernelUpdateHead, KernelUpdator
from .lraspp_head import LRASPPHead
from .nl_head import NLHead
from .ocr_head import OCRHead
from .point_head import PointHead
from .psa_head import PSAHead
from .psp_head import PSPHead
from .segformer_head import SegformerHead
from .segmenter_mask_head import SegmenterMaskTransformerHead
from .sep_aspp_head import DepthwiseSeparableASPPHead
from .sep_fcn_head import DepthwiseSeparableFCNHead
from .setr_mla_head import SETRMLAHead
from .setr_up_head import SETRUPHead
from .stdc_head import STDCHead
from .uper_head import UPerHead
from .aspp_head_se import SeASPPHead
from .sppm_head import SPPMHead
from .aspp_head_lite import LiteASPPHead
from .mobilev3_sppm import MobilenetASPPHead
from .mobilev3_small_sppm import MobilenetSmallASPPHead
from .ddrnet_decode import DdrNetHead
from .cross_se import LiteAsppCrossSe
from .cross_se_besinet import LiteAsppCrossSeBisenet
from .bisenet_sppm import BiseNetASPPHead
from .Fld_UAFM import FldUAFMHead
from .cross_cbam_bisenet import CrosseCbamHead
from .aspp_head_se import SeASPPHead
from .cross_se_besinet_li import LiteAsppCrossSeBisenetLi
__all__ = [
    'FCNHead', 'PSPHead', 'ASPPHead', 'PSAHead', 'NLHead', 'GCHead', 'CCHead',
    'UPerHead', 'DepthwiseSeparableASPPHead', 'ANNHead', 'DAHead', 'OCRHead',
    'EncHead', 'DepthwiseSeparableFCNHead', 'FPNHead', 'EMAHead', 'DNLHead',
    'PointHead', 'APCHead', 'DMHead', 'LRASPPHead', 'SETRUPHead',
    'SETRMLAHead', 'DPTHead', 'SETRMLAHead', 'SegmenterMaskTransformerHead',
    'SegformerHead', 'ISAHead', 'STDCHead', 'IterativeDecodeHead',
    'KernelUpdateHead', 'KernelUpdator', 'SeASPPHead', 'SPPMHead', 'LiteASPPHead',
    'MobilenetASPPHead', 'MobilenetSmallASPPHead', 'DdrNetHead', 'LiteAsppCrossSe',
    'LiteAsppCrossSeBisenet', 'BiseNetASPPHead', 'FldUAFMHead', 'CrosseCbamHead',
    'SeASPPHead', 'LiteAsppCrossSeBisenetLi'
]
