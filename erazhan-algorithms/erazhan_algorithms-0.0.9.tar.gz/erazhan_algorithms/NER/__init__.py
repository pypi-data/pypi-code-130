# -*- coding = utf-8 -*-
# @time: 2022/3/1 4:13 下午
# @Author: erazhan
# @File: __init__.py

# ----------------------------------------------------------------------------------------------------------------------
from .models import Bert4NER, init_ner_model
from .train import train_ner
from .predict import predict_on_batch_ner, eval_ner

from .utils import NER_DEFAULT_PARAM_DICT,NER_OTHER_PARAM_DICT,get_ner_parser