# -*- coding = utf-8 -*-
# @time: 2022/3/4 3:18 下午
# @Author: erazhan
# @File: main_qa.py

# ----------------------------------------------------------------------------------------------------------------------
import os
import copy

import pandas as pd
from tqdm import tqdm
from transformers import BertTokenizer

from erazhan_utils import read_json_file

from erazhan_algorithms.QA import init_qa_model, train_qa,eval_qa,predict_on_batch_qa
from erazhan_algorithms.QA import get_qa_params_help,get_qa_parser,QA_DEFAULT_PARAM_DICT,QA_OTHER_PARAM_DICT
from erazhan_algorithms.QA import generate_qa_tokens

QA_DEFAULT_PARAM_DICT = {"gpu": 0,
                         "maxlen": 256,
                         "batch_size": 64,
                         "predict_batch_size": 4,
                         "learning_rate": 2e-5,
                         "warmup_proportion": 0.1,
                         "epochs": 3,
                         "save_steps": 500,
                         "print_steps": 20,
                         "disable": False,
                         "doc_token": "[DOCTOR]"}

QA_OTHER_PARAM_DICT = {"bert_model": "/home/zhanjiyuan/code/pretrained_model/chinese-roberta-wwm-ext",
                         "train_file": "./data/emr_qa_train_jtks.json", # test_train_qa_v1.json
                         "eval_file": "./data/emr_qa_eval_jtks.json",
                         "output_dir": "./model_qa_emr_all",
                         "predict_dir": "./model_qa_emr_all",
                         }

os.environ["CUDA_VISIBLE_DEVICES"] = "%d"%QA_DEFAULT_PARAM_DICT["gpu"]

def train_or_eval_from_eralgo(mode = "train"):

    param_dict = copy.deepcopy(QA_DEFAULT_PARAM_DICT)
    param_dict.update(QA_OTHER_PARAM_DICT)

    qa_args = get_qa_parser(param_dict)
    tokenizer = BertTokenizer.from_pretrained(qa_args.bert_model)

    train_data = read_json_file(param_dict["train_file"])
    eval_data = read_json_file(param_dict["eval_file"])

    # return
    if mode == "train":
        kwargs = {"args": qa_args,
                  "train_data": train_data,
                  "eval_data": eval_data,
                  "tokenizer": tokenizer}
        train_qa(**kwargs)
    elif mode == "eval":
        eval_kwargs = {"args": qa_args, "tokenizer": tokenizer}
        model = init_qa_model(qa_args, from_scratch = False)
        eval_qa(model,eval_data,**eval_kwargs)
        # eval_qa(model, text_list = eval_text, label_list = eval_intent_labels, **eval_kwargs)
    elif mode == "jt":

        model = init_qa_model(qa_args, from_scratch=False)
        model.eval()

        for_intent_list = ["询问身高","询问体重","询问过敏史","询问体温"]
        question = "孩子的身高体重是多少？"
        question = "孩子发烧多少度了"
        answer = "172cm,98斤"
        answer = "65"

        data_list = []
        for one_intent in for_intent_list:
            one_data = generate_qa_tokens(question=question, answer = answer,maxlen = qa_args.maxlen, question_intent = one_intent)
            data_list.append(one_data)

        eval_kwargs = {"args": qa_args, "tokenizer": tokenizer}
        start_target_list, end_target_list = predict_on_batch_qa(model, data_list, **eval_kwargs)

        for i,one_data in enumerate(data_list):
            tokens = one_data["tokens"]
            start_pos = start_target_list[i]
            end_pos = end_target_list[i]

            pred_entity = "".join(tokens[start_pos:end_pos+1])
            print("tokens:\n",tokens)
            print("pred_entity:\n",pred_entity, start_pos, end_pos)
            print("-"*50)

    elif mode == "predict_emr_data":
        data_file = "/home/zhanjiyuan/code/EMR/data/qa/train_emr_qa_all_v4.json"
        predict_intent_list = ["询问身高","询问体重"]

        train_data_list = read_json_file(data_file)
        train_data_list = train_data_list[:1000]

        eval_kwargs = {"args": qa_args, "tokenizer": tokenizer}

        model = init_qa_model(qa_args, from_scratch=False)

        final_data_list = []
        final_question_list = []
        final_answer_list = []
        # final_intent_list = []
        # final_belong_list = []
        i = 0

        for one_data in tqdm(train_data_list, desc = "generate data tokens"):

            question = one_data["问题"]
            answer = one_data["回答"]

            final_question_list.append(question)
            final_answer_list.append(answer)

            for one_intent in predict_intent_list:

                one_data = generate_qa_tokens(question=question, answer = answer,maxlen = qa_args.maxlen, question_intent = one_intent)
                final_data_list.append(one_data)

                # final_intent_list.append(one_intent)
                # final_belong_list.append(i)

            i+=1

        start_target_list, end_target_list = predict_on_batch_qa(model, final_data_list, **eval_kwargs)
        final_hei_entity_list = []
        final_wei_entity_list = []

        assert len(final_data_list)%2==0

        for i in range(len(final_data_list)//2):

            assert type(i)==int
            one_data = final_data_list[2*i]

            tokens = one_data["tokens"]

            start_pos_hei = start_target_list[2*i]
            end_pos_hei = end_target_list[2*i]

            start_pos_wei = start_target_list[2 * i + 1]
            end_pos_wei = end_target_list[2 * i + 1]

            pred_hei_entity = "".join(tokens[start_pos_hei:end_pos_hei+1])
            pred_wei_entity = "".join(tokens[start_pos_wei:end_pos_wei + 1])

            final_hei_entity_list.append(pred_hei_entity)
            final_wei_entity_list.append(pred_wei_entity)

            # print("tokens:\n",tokens)
            # print("pred_entity:\n",pred_entity, start_pos, end_pos)
            # print("-"*50)

    # final_columns = ["belong_index_in_v4","问题","回答","意图","predict_entity"]

    # final_dict = {
    #               "question":final_question_list,
    #               "answer":final_answer_list,
    #               "height":final_hei_entity_list,
    #                 "weight":final_wei_entity_list
    #               }
    #
    # final_df = pd.DataFrame(final_dict)
    # savename = "./data/save_pred_all_new.csv"
    # final_df.to_csv(savename,encoding='gb18030',index=False)

if __name__ == "__main__":

    get_qa_params_help()
    mode = "train"
    # mode = "eval"
    # mode = "test"
    mode = "jt"
    # mode = "predict_emr_data"
    train_or_eval_from_eralgo(mode = mode)

    pass

