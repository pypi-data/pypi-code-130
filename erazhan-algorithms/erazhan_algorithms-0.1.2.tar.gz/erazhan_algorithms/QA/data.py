# -*- coding = utf-8 -*-
# @time: 2022/3/3 6:32 下午
# @Author: erazhan
# @File: data.py

# ----------------------------------------------------------------------------------------------------------------------
from tqdm import tqdm
import copy
from erazhan_algorithms.constants import CLS_TOKEN, SEP_TOKEN

def convert_to_inputdata_qa(tokenizer, data_list, maxlen = 512, mode = "train", disable = False, doc_token = "[DOCTOR]"):

    '''
    :param tokenizer
    :param data_list, 必须包括tokens字段, tokens列表中必须包括SEP_TOKEN = "[SEP]"
    :param maxlen,
    :param disable, False
    :param mode, train, eval(必须包括offsets), test
    :param doc_token, 用于标记抽取不出结果的数据，默认为[DOCTOR],可自定义，当vocab.txt中需要增加相应的token, 将其放在cls_token="[CLS]"之后
    :return: final_data_list: 每条数据必须包含tokens, input_ids, segment_ids, mode = train or eval则还要包括start_position_label, end_position_label
    '''

    data_dict = {"tokens":[],
                 "input_ids":[],
                 "input_masks":[],
                 "segment_ids":[]}

    final_data_list = []
    for one_data in tqdm(data_list, desc = "convert_to_inputdata_qa", disable=disable):

        tem_data = copy.deepcopy(data_dict)
        tem_tokens = one_data["tokens"]
        tem_tokens.insert(1, doc_token)
        tem_data["tokens"] = tem_tokens

        input_ids = tokenizer.convert_tokens_to_ids(tem_tokens)
        first_sep_index = tem_tokens.index(SEP_TOKEN)
        segment_ids = [0] * (first_sep_index + 1) + [1] * (len(tem_data['tokens']) - first_sep_index - 1)
        input_masks = [1] * len(input_ids)

        while len(input_ids) < maxlen:
            input_ids.append(0)
            input_masks.append(0)
            segment_ids.append(0)

        tem_data['input_ids'] = input_ids
        tem_data['segment_ids'] = segment_ids
        tem_data['input_masks'] = input_masks

        if mode == "train" or mode == "eval":

            start_position_label,end_position_label = 0,0 # -1改成0

            if len(one_data["offsets"]):
                assert one_data["offsets"][0] <= one_data["offsets"][1]
                start_position_label = one_data["offsets"][0]
                end_position_label = one_data["offsets"][1]

            tem_data["start_position_label"] = start_position_label + 1 # 添加doc_token用于标记为预测成空字符,
            tem_data["end_position_label"] = end_position_label + 1

        final_data_list.append(tem_data)

    return final_data_list

def trans_inputdata_qa(data_list, mode = "train", disable = False):

    all_input_ids, all_input_masks, all_segment_ids = [], [], []

    if mode == "train" or mode == "eval":
        all_start_position_labels = []
        all_end_position_labels = []

    for one_data in tqdm(data_list,desc = 'trans_inputdata_qa',disable = disable):
        all_input_ids.append(one_data["input_ids"])
        all_input_masks.append(one_data["input_masks"])
        all_segment_ids.append(one_data["segment_ids"])
        if mode == "train" or mode == "eval":
            all_start_position_labels.append(one_data['start_position_label'])
            all_end_position_labels.append(one_data['end_position_label'])

    result = [all_input_ids,all_input_masks,all_segment_ids]

    if mode == "train" or mode == "eval":
        result.extend([all_start_position_labels,all_end_position_labels])

    return result

def generate_qa_tokens(question, answer, maxlen = 512, question_intent = ""):

    """用于预测时生成初步的token, 不包括doc_token='[DOCTOR]'"""
    tokens = [CLS_TOKEN] + [e for e in question_intent] + [SEP_TOKEN] + [e for e in question] + [SEP_TOKEN] + [e for e in answer] + [SEP_TOKEN]
    if len(tokens) > maxlen:
        tokens = tokens[:maxlen - 1]
        tokens.append(SEP_TOKEN)

    one_data = {"question": question, "answer": answer, "tokens": tokens}

    return one_data

if __name__ == "__main__":

    pass
