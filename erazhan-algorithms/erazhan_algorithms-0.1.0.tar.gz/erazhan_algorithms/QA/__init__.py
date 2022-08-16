# -*- coding = utf-8 -*-
# @time: 2022/3/1 4:13 下午
# @Author: erazhan
# @File: __init__.py

# ----------------------------------------------------------------------------------------------------------------------
#
from .models import Bert4QA, init_qa_model
from .train import train_qa
from .predict import predict_on_batch_qa, eval_qa
from .data import convert_to_inputdata_qa, trans_inputdata_qa, generate_qa_tokens

from .utils import QA_DEFAULT_PARAM_DICT, QA_OTHER_PARAM_DICT, get_qa_parser, get_qa_params_help