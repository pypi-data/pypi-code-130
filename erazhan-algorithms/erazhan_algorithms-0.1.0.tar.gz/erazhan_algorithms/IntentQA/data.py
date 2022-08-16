# -*- coding = utf-8 -*-
# @time: 2022/3/7 3:25 下午
# @Author: erazhan
# @File: data.py

# ----------------------------------------------------------------------------------------------------------------------
from tqdm import tqdm
from erazhan_algorithms.constants import CLS_TOKEN, SEP_TOKEN

def convert_to_inputdata_intentqa(tokenizer, data_list, intent_vocab, maxlen = 512, mode="train", disable=False):

    '''
    :param tokenizer
    :param data_list
    :param max_seq_length
    :return: new_data_list, 在data_list的基础上增加input_ids,segment_ids等
    '''

    final_data_list = []

    for one_data in tqdm(data_list, desc = "convert_to_inputdata_intentqa", disable = disable):

        tem_data = {}
        tem_data["tokens"] = one_data["tokens"]

        input_ids = tokenizer.convert_tokens_to_ids(tem_data['tokens'])
        first_sep_index = tem_data['tokens'].index(SEP_TOKEN)

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

            tem_data['intent_labels'] = [0] * len(intent_vocab)
            # 没有数据的位置上起始点均标记为-1

            tem_data['start_position_labels'] = [-1] * len(intent_vocab)
            tem_data['end_position_labels'] = [-1] * len(intent_vocab)

            for one_intent in intent_vocab:

                tem_entities = one_data[one_intent]['entities']
                tem_offsets = one_data[one_intent]['offsets']

                # 长度需要与maxlen保持一致
                if len(tem_entities):
                    intent_pos = intent_vocab.index(one_intent)
                    tem_data['intent_labels'][intent_pos] = 1
                    # print(one_intent,tem_offsets)
                    # print(one_data)
                    # print("-"*100)
                    for one_offset in tem_offsets:

                        start, end = one_offset
                        tem_data['start_position_labels'][intent_pos] = start
                        tem_data['end_position_labels'][intent_pos] = end

        final_data_list.append(tem_data)

    return final_data_list

def trans_inputdata_intentqa(data_list, mode = "train", disable = False):

    '''
    :param data_list:
    :param mode: train or eval or test, test -> 数据没有label
    :return:
    '''

    all_input_ids, all_input_masks, all_segment_ids = [], [], []

    if mode == "train" or mode == "eval":
        all_intent_labels = []
        all_start_position_tag_labels = []
        all_end_position_tag_labels = []

    for one_data in tqdm(data_list,desc = 'trans_inputdata_intentqa',disable = disable):

        all_input_ids.append(one_data["input_ids"])
        all_input_masks.append(one_data["input_masks"])
        all_segment_ids.append(one_data["segment_ids"])
        if mode == "train" or mode == "eval":
            all_intent_labels.append(one_data["intent_labels"])
            # all_tag_labels.append(one_data["tag_labels"])
            all_start_position_tag_labels.append(one_data['start_position_labels'])
            all_end_position_tag_labels.append(one_data['end_position_labels'])

    result = [all_input_ids,all_input_masks,all_segment_ids]

    if mode == "train" or mode == "eval":
        # result.extend([all_intent_labels,all_tag_labels])
        result.extend([all_intent_labels,all_start_position_tag_labels,all_end_position_tag_labels])

    return result

def generate_intentqa_tokens(question, answer, maxlen = 512):

    """用于预测时生成初步的tokens"""
    tokens = [CLS_TOKEN] + [e for e in question] + [SEP_TOKEN] + [e for e in answer] + [SEP_TOKEN]
    if len(tokens) > maxlen:
        tokens = tokens[:maxlen - 1]
        tokens.append(SEP_TOKEN)

    one_data = {"问题": question, "回答": answer, "tokens": tokens}

    return one_data

if __name__ == "__main__":

    pass
