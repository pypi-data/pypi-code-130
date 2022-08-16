# -*- coding = utf-8 -*-
# @time: 2022/3/7 3:23 下午
# @Author: erazhan
# @File: main_miqa.py

# ----------------------------------------------------------------------------------------------------------------------

'''此工具仅用于自己使用(电子病历历史版本)'''

import os
import copy

import pandas as pd
from tqdm import tqdm
from transformers import BertTokenizer

from erazhan_utils import read_json_file,save_json_file

from erazhan_algorithms.IntentQA import init_intentqa_model, train_intentqa,eval_intentqa,predict_on_batch_intentqa
from erazhan_algorithms.IntentQA import get_intentqa_params_help,get_intentqa_parser,IntentQA_DEFAULT_PARAM_DICT,IntentQA_OTHER_PARAM_DICT
# from erazhan_algorithms.IntentQA import generate_intentqa_tokens

intent_vocab = ["询问既往史","询问家族史","询问过敏史","询问手术史","询问生理期","询问备孕期","询问妊娠期","询问哺乳期","询问生育","询问体温","询问身高","询问体重","医生诊断","医生建议"]

IntentQA_DEFAULT_PARAM_DICT = {"gpu": 0,
                         "maxlen": 256,
                         "batch_size": 64,
                         "predict_batch_size": 4,
                         "learning_rate": 2e-5,
                         "warmup_proportion": 0.1,
                         "epochs": 5,
                         "save_steps": 500,
                         "print_steps": 20,
                         "disable": False
                         }

IntentQA_OTHER_PARAM_DICT = {"bert_model": "/home/zhanjiyuan/code/pretrained_model/chinese-roberta-wwm-ext",
                         "train_file": "/home/zhanjiyuan/code/EMR_offline/data/qa/train_emr_qa_v3_arti.json",
                         "eval_file": "/home/zhanjiyuan/code/EMR_offline/data/qa/eval_emr_qa_v3_arti.json",
                         "intent_vocab": intent_vocab,
                         "num_intents":len(intent_vocab),
                         "output_dir": "./model_intentqa_e5_arti",
                         "predict_dir": "./model_intentqa_e5_arti",
                         }

os.environ["CUDA_VISIBLE_DEVICES"] = "%d"%IntentQA_DEFAULT_PARAM_DICT["gpu"]

def train_or_eval_from_eralgo(mode = "train"):

    param_dict = copy.deepcopy(IntentQA_DEFAULT_PARAM_DICT)
    param_dict.update(IntentQA_OTHER_PARAM_DICT)

    intentqa_args = get_intentqa_parser(param_dict)
    tokenizer = BertTokenizer.from_pretrained(intentqa_args.bert_model)

    train_data = read_json_file(param_dict["train_file"])
    eval_data = read_json_file(param_dict["eval_file"])

    # return
    if mode == "train":
        kwargs = {"args": intentqa_args,
                  "train_data": train_data,
                  "eval_data": eval_data,
                  "tokenizer": tokenizer}
        train_intentqa(**kwargs)
    elif mode == "eval":
        eval_kwargs = {"args": intentqa_args, "tokenizer": tokenizer}
        model = init_intentqa_model(intentqa_args, from_scratch = False)
        eval_intentqa(model,eval_data,**eval_kwargs)

if __name__ == "__main__":

    mode = "train"
    # mode = "eval"
    # mode = "test"
    train_or_eval_from_eralgo(mode = mode)

    pass
