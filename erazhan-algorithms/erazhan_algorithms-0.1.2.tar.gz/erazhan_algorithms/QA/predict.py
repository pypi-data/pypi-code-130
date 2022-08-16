# -*- coding = utf-8 -*-
# @time: 2022/3/3 6:32 下午
# @Author: erazhan
# @File: predict.py

# ----------------------------------------------------------------------------------------------------------------------
from tqdm import tqdm
import torch
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from transformers import BertTokenizer

from .data import convert_to_inputdata_qa,trans_inputdata_qa
from .models import init_qa_model

def predict_on_batch_qa(model, data_list, **kwargs):

    '''tokenizer'''
    assert "args" in kwargs.keys()

    args = kwargs["args"]

    tokenizer = BertTokenizer.from_pretrained(args.bert_model) if "tokenizer" not in kwargs.keys() else kwargs["tokenizer"]

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if model is None:
        model = init_qa_model(args, from_scratch = True)

    InputData_list = convert_to_inputdata_qa(tokenizer, data_list, maxlen = args.maxlen, mode="test",disable=args.disable, doc_token = args.doc_token)
    all_input_ids, all_input_masks, all_segment_ids = trans_inputdata_qa(InputData_list, mode="test", disable=args.disable)

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)
    all_segment_ids = torch.tensor(all_segment_ids, dtype=torch.long).to(device)

    eval_data = TensorDataset(all_input_ids, all_input_masks,all_segment_ids)
    eval_sampler = SequentialSampler(eval_data)
    eval_dataloader = DataLoader(eval_data, sampler=eval_sampler,
                                 batch_size = args.predict_batch_size)

    model.eval()

    start_target_list = []
    end_target_list = []

    for input_ids, input_mask, segment_ids in tqdm(eval_dataloader, desc='qa predict',disable = args.disable):
        input_ids = input_ids.to(device)
        input_mask = input_mask.to(device)
        segment_ids = segment_ids.to(device)

        with torch.no_grad():
            # [bsz, maxlen], [bsz, maxlen]
            start_logits, end_logits = model(input_ids=input_ids, attention_mask=input_mask, token_type_ids=segment_ids)

            start_logits = F.softmax(start_logits.detach().cpu(), dim=1)  # [bsz,maxlen]
            start_result = torch.max(start_logits, dim=1, keepdims=False)
            start_pred_target = start_result.indices.tolist()
            start_target_list.extend(start_pred_target)

            end_logits = F.softmax(end_logits.detach().cpu(), dim=1)
            end_result = torch.max(end_logits, dim=1, keepdims=False)
            end_pred_target = end_result.indices.tolist()
            end_target_list.extend(end_pred_target)

    return start_target_list, end_target_list

def eval_qa(model, data_list,select_print_n = 100, **kwargs):

    start_label_list = []
    end_label_list = []

    for one_data in data_list:
        start_pos,end_pos = one_data["offsets"]
        start_label_list.append(start_pos)
        end_label_list.append(end_pos)

    start_target_list,end_target_list = predict_on_batch_qa(model, data_list, **kwargs)

    N = len(start_label_list)

    print("start true and predict first %d:\n %s \n %s" % (min(select_print_n,N),start_label_list[:select_print_n], start_target_list[:select_print_n]))
    print("end true and predict first %d:\n %s \n %s" % (min(select_print_n,N),end_label_list[:select_print_n], end_target_list[:select_print_n]))

    correct_cnt = 0
    error_cnt = 0

    for i in range(N):

        question = data_list[i]["question"]
        answer = data_list[i]["answer"]
        tokens = data_list[i]["tokens"]

        true_start = start_label_list[i]
        true_end = end_label_list[i]

        pred_start = start_target_list[i]
        pred_end = end_target_list[i]

        true_entity = "".join(tokens[true_start+1:true_end+1+1])
        pred_entity = "".join(tokens[pred_start:pred_end+1])

        if true_start + 1 == pred_start and true_end + 1 == pred_end:
            correct_cnt += 1
            true_flag = True
        else:
            error_cnt += 1
            true_flag = False

        if "intent" in data_list[i].keys():
            intent = data_list[i]["intent"]
            print("%d -> %s -> %s -> %s"%(i+1,intent,question,answer))
        else:
            print("%d -> %s -> %s"%(i+1,question,answer))
        if not true_flag:
            print("predict error")
        print("correct: %d, error: %d"%(correct_cnt, error_cnt))
        print("true_entity: %s"%(true_entity))
        print("pred_entity: %s"%(pred_entity))
        print("-"*50)

    print("Accuracy:", correct_cnt / N)

if __name__ == "__main__":

    pass
