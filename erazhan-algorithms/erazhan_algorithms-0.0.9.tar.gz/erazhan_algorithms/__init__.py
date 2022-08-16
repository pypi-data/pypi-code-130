# -*- coding = utf-8 -*-
# @time: 2022/2/24 10:54 上午
# @Author: erazhan
# @File: __init__.py

# ----------------------------------------------------------------------------------------------------------------------

__version__ = "0.0.9"

from . import TC, MITC, NER, QA, constants, IntentQA

from .TC.train import warmup_linear
from .TC.utils import TC_DEFAULT_PARAM_DICT, TC_OTHER_PARAM_DICT
from .MITC.utils import MITC_DEFAULT_PARAM_DICT, MITC_OTHER_PARAM_DICT
from .QA.utils import QA_DEFAULT_PARAM_DICT, QA_OTHER_PARAM_DICT
from .IntentQA.utils import IntentQA_DEFAULT_PARAM_DICT, IntentQA_OTHER_PARAM_DICT
from .NER.utils import NER_DEFAULT_PARAM_DICT,NER_OTHER_PARAM_DICT

from .constants import CLS_TOKEN, SEP_TOKEN, PAD_TOKEN, DOC_TOKEN

# from erazhan_algorithms import *, 如果定义了__all__, 则导入当中的变量等, 否则导入所有变量
__all__ = ["TC", "MITC", "NER", "QA","IntentQA", "warmup_linear",
           "TC_DEFAULT_PARAM_DICT", "TC_OTHER_PARAM_DICT",
           "MITC_DEFAULT_PARAM_DICT", "MITC_OTHER_PARAM_DICT",
           "QA_DEFAULT_PARAM_DICT", "QA_OTHER_PARAM_DICT",
           "IntentQA_DEFAULT_PARAM_DICT", "IntentQA_OTHER_PARAM_DICT",
           "NER_DEFAULT_PARAM_DICT","NER_OTHER_PARAM_DICT",
           "CLS_TOKEN", "SEP_TOKEN","PAD_TOKEN","DOC_TOKEN"]