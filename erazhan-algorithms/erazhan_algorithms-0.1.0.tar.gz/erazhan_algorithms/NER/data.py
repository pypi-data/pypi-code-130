# -*- coding:utf-8 -*-
# @time: 2022/6/28 4:44 下午
# @Author: erazhan
# @File: data.py

# ----------------------------------------------------------------------------------------------------------------------
from tqdm import tqdm

class InputData_ner(object):

    def __init__(self,
                 unique_id,
                 text,
                 tokens,
                 input_ids,
                 input_masks,
                 segment_ids = None,
                 tag_labels = None,
                 # length = None
                 ): # 可不用segment_ids
        self.unique_id = unique_id
        self.text = text
        self.tokens = tokens
        self.input_ids = input_ids
        self.input_masks = input_masks
        self.segment_ids = segment_ids
        self.tag_labels = tag_labels

def convert_to_inputdata_ner(tokenizer, text_list, tag_list = None, tag2id = None, maxlen = 512,disable = False):

    # 用户输入的maxlen不包括[CLS]和[SEP], 需要预留两个位置
    assert type(maxlen) == int, "type(maxlen) % is error"%type(maxlen)
    maxlen = maxlen + 2
    maxlen = min(maxlen, 512)

    # ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    InputData_list = []

    for unique_id in tqdm(range(len(text_list)), desc="convert_to_inputdata_ner", disable=disable):

        text = text_list[unique_id]
        text = text[:maxlen - 2]

        if tag_list is not None:
            tags = tag_list[unique_id]
            tags = tags[:maxlen - 2]
            tags = [tag2id[oe] for oe in tags]
        else:
            tags = None

        # text -> tokens
        # 不再考虑转为小写
        # tokens = [e.lower() if e in ABC else e for e in text]
        tokens = [e for e in text]
        tokens.insert(0, "[CLS]")
        tokens.append("[SEP]")

        # 补充tags首末数字
        if tags is not None:
            tags.insert(0, 0)
            tags.append(0)

        # input_ids
        input_ids = tokenizer.convert_tokens_to_ids(tokens)
        # length = len(input_ids) # 包括[CLS]和[SEP]

        input_masks = [1] * len(tokens)

        while len(input_ids) < maxlen:

            input_ids.append(0)
            input_masks.append(0)

            if tags is not None:
                tags.append(0)


        # segment_ids可以不提供
        segment_ids = [0] * len(input_ids)

        one_inputdata = InputData_ner(unique_id = unique_id,
                                      text = text,
                                      tokens = tokens,
                                      input_ids = input_ids,
                                      input_masks = input_masks,
                                      segment_ids = segment_ids,
                                      tag_labels = tags,
                                      )

        InputData_list.append(one_inputdata)

    return InputData_list

def trans_inputdata_ner(InputData_list, mode = "train", disable = False):

    '''
    :param InputData_list:
    :param mode: train or eval or test, test -> 数据没有label
    :return:
    '''

    all_input_ids, all_input_masks, all_segment_ids = [], [], []
    # all_lengths = []

    all_tags = []

    for one_inputdata in tqdm(InputData_list, desc = "trans_inputdata", disable = disable):

        all_input_ids.append(one_inputdata.input_ids)
        all_input_masks.append(one_inputdata.input_masks)
        all_segment_ids.append(one_inputdata.segment_ids)

        # all_lengths.append(one_inputdata.length)

        if mode == "train" or mode == "eval":
            all_tags.append(one_inputdata.tag_labels)

    result = [all_input_ids,all_input_masks,all_segment_ids]

    if mode == "train" or mode == "eval":

        result.append(all_tags)

    return result

if __name__ == "__main__":
    pass