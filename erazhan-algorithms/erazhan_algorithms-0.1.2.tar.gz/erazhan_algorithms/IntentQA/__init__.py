# -*- coding = utf-8 -*-
# @time: 2022/3/7 1:44 下午
# @Author: erazhan
# @File: __init__.py

# ----------------------------------------------------------------------------------------------------------------------

from .models import Bert4IntentQA, init_intentqa_model
from .train import train_intentqa
from .predict import predict_on_batch_intentqa, eval_intentqa
from .data import convert_to_inputdata_intentqa, trans_inputdata_intentqa, generate_intentqa_tokens

from .utils import IntentQA_DEFAULT_PARAM_DICT, IntentQA_OTHER_PARAM_DICT, get_intentqa_parser, get_intentqa_params_help
