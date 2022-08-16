# -*- coding:utf-8 -*-
# @time: 2022/6/28 4:44 下午
# @Author: erazhan
# @File: predict.py

# ----------------------------------------------------------------------------------------------------------------------
from tqdm import tqdm
import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from transformers import BertTokenizer

from .data import convert_to_inputdata_ner, trans_inputdata_ner
from .models import init_ner_model
from .utils import search_entity

def recover_tag(tag_logits, tag_mask_tensor, id2tag):

    max_seq_len = tag_logits.size(0)
    tags = []

    for j in range(max_seq_len):
        if tag_mask_tensor[j] == 1:
            value, tag_id = torch.max(tag_logits[j], dim=-1)
            tags.append(id2tag[tag_id.item()])

    return tags

def predict_on_batch_ner(model, text_list, **kwargs):

    '''tokenizer'''
    assert "args" in kwargs.keys()

    args = kwargs["args"]
    maxlen = args.maxlen

    batch_size = args.predict_batch_size

    tokenizer = BertTokenizer.from_pretrained(args.bert_model) if "tokenizer" not in kwargs.keys() else kwargs["tokenizer"]

    InputData_list = convert_to_inputdata_ner(tokenizer, text_list=text_list, tag_list=None, tag2id = None, maxlen=maxlen, disable=args.disable)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if model is None:
        model = init_ner_model(args, from_scratch = False)

    all_input_ids, all_input_masks, all_segment_ids = trans_inputdata_ner(InputData_list, mode = 'test',disable = args.disable)

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)
    all_segment_ids = torch.tensor(all_segment_ids, dtype=torch.long).to(device)

    eval_data = TensorDataset(all_input_ids, all_input_masks, all_segment_ids)
    eval_sampler = SequentialSampler(eval_data)
    eval_dataloader = DataLoader(eval_data, sampler=eval_sampler,
                                 batch_size = args.predict_batch_size)

    model.eval()

    all_predict_entity_list = []

    with torch.no_grad():

        for step, batch in enumerate(tqdm(eval_dataloader, desc = "ner predict", disable=args.disable)):

            input_ids, input_masks, segment_ids = batch

            batch_tag_logits = model(input_ids=input_ids,
                                     attention_mask=input_masks,
                                     token_type_ids=segment_ids,
                                     )

            batch_tag_logits = batch_tag_logits[0]
            real_batch_size = batch_tag_logits.shape[0]

            for i in range(real_batch_size):

                input_mask = input_masks[i]

                predict_tags = recover_tag(batch_tag_logits[i], input_mask,args.ner_id2tag)

                the_inputdata = InputData_list[i + step * batch_size]
                tokens = the_inputdata.tokens[:]

                del predict_tags[-1], predict_tags[0]
                del tokens[-1], tokens[0]

                predict_entities = search_entity(tokens, predict_tags)

                all_predict_entity_list.append(predict_entities)

    return all_predict_entity_list

def eval_ner(model, text_list, tag_list, **kwargs):

    # 计算完全相等的准确率
    # kwargs = {"args":None, "tokenizer":None}
    all_predict_entity_list = predict_on_batch_ner(model, text_list, **kwargs)
    all_true_entity_list = []

    for one_tag,one_text in zip(tag_list,text_list):
        one_tokens = [e for e in one_text]
        one_true_result = search_entity(one_tokens,one_tag)
        all_true_entity_list.append(one_true_result)

    error_cnt = 0
    for true_entity,pred_entity,the_text in zip(all_true_entity_list,all_predict_entity_list,text_list):

        equal_flag = True

        if len(true_entity)!=len(pred_entity):
            print("len error")
            equal_flag = False
        else:
            # 在search_entity中做过排序
            for one_te,one_pe in zip(true_entity,pred_entity):
                if one_te["text"]!=one_pe["text"] or one_te["offset"]!=one_pe["offset"]:
                    print("text error")
                    equal_flag = False
                    break

        if not equal_flag:
            error_cnt += 1
            print("text:",the_text)
            print("true_entity:",true_entity)
            print("pred_entity:",pred_entity)
            print("-"*100)

    print("Accuracy:", (1 - error_cnt/len(text_list)))

if __name__ == "__main__":

    pass