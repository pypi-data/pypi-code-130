# -*- coding = utf-8 -*-
# @time: 2022/3/7 3:22 下午
# @Author: erazhan
# @File: predict.py

# ----------------------------------------------------------------------------------------------------------------------
from tqdm import tqdm
import torch
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from transformers import BertTokenizer

from .data import convert_to_inputdata_intentqa,trans_inputdata_intentqa
from .models import init_intentqa_model

def predict_on_batch_intentqa(model, data_list,**kwargs):

    '''data_list: [one_data,...,]
    one_data: ["问题":"身高","回答":"172cm","tokens":[]]
    '''

    assert "args" in kwargs.keys()
    args = kwargs["args"]
    intent_vocab = args.intent_vocab

    tokenizer = BertTokenizer.from_pretrained(args.bert_model) if "tokenizer" not in kwargs.keys() else kwargs["tokenizer"]

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if model is None:
        model = init_intentqa_model(args, from_scratch=True)

    InputData_list = convert_to_inputdata_intentqa(tokenizer, data_list, intent_vocab, maxlen=args.maxlen, mode="test", disable=args.disable)
    all_input_ids, all_input_masks, all_segment_ids = trans_inputdata_intentqa(InputData_list, mode="test", disable=args.disable)

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)
    all_segment_ids = torch.tensor(all_segment_ids, dtype=torch.long).to(device)

    eval_data = TensorDataset(all_input_ids, all_input_masks, all_segment_ids)
    eval_sampler = SequentialSampler(eval_data)
    eval_dataloader = DataLoader(eval_data, sampler=eval_sampler,
                                 batch_size=args.predict_batch_size)

    step = 0
    predict_intent_dict = {i: [] for i in range(len(args.intent_vocab))}
    predict_start_dict = {i: [] for i in range(len(args.intent_vocab))}
    predict_end_dict = {i: [] for i in range(len(args.intent_vocab))}

    for input_ids, input_mask, segment_ids in tqdm(eval_dataloader, desc='intentqa predict', disable=args.disable):

        input_ids = input_ids.to(device)
        input_mask = input_mask.to(device)
        segment_ids = segment_ids.to(device)

        with torch.no_grad():

            intent_logits, start_end_logits = model(input_ids=input_ids, attention_mask=input_mask,
                                                    token_type_ids=segment_ids)

            for i in range(len(args.intent_vocab)):
                one_intent_logit = intent_logits[i]  # error: [bsz, num_intents] -> [bsz, 2]
                one_start_logit = start_end_logits[i]
                one_end_logit = start_end_logits[i + 1]

                one_intent_logit = F.softmax(one_intent_logit.detach().cpu(), dim=1)
                one_intent_result = torch.max(one_intent_logit, dim=1, keepdims=False)

                one_pred_intent_target = one_intent_result.indices.tolist()  # [bsz,]

                predict_intent_dict[i].extend(one_pred_intent_target)

                # ------------------------------------------------------------------------------------------------------
                one_start_logit = F.softmax(one_start_logit.detach().cpu(), dim=1)
                one_start_result = torch.max(one_start_logit, dim=1, keepdims=False)
                one_start_pred_target = one_start_result.indices.tolist()

                one_end_logit = F.softmax(one_end_logit.detach().cpu(), dim=1)
                one_end_result = torch.max(one_end_logit, dim=1, keepdims=False)
                one_end_pred_target = one_end_result.indices.tolist()

                predict_start_dict[i].extend(one_start_pred_target)
                predict_end_dict[i].extend(one_end_pred_target)

        step += 1

    predict_result = []

    for b_i in range(len(data_list)):
        predict_result.append({one_intent: ["取值", "标签"] for one_intent in args.intent_vocab})

    for i, intent_name in enumerate(args.intent_vocab):

        for b_i in range(len(data_list)):
            tokens = data_list[b_i]['tokens']

            start_position = predict_start_dict[i][b_i]
            end_position = predict_end_dict[i][b_i]

            entity = "".join(tokens[start_position:end_position + 1])
            label = predict_intent_dict[i][b_i]

            predict_result[b_i][intent_name][0] = entity
            predict_result[b_i][intent_name][1] = label

    return predict_result

def eval_intentqa(model, data_list, **kwargs):

    assert "args" in kwargs.keys()

    args = kwargs["args"]
    intent_vocab = args.intent_vocab
    predict_result = predict_on_batch_intentqa(model, data_list, **kwargs)
    N = len(data_list)

    correct_cnt = 0
    all_cnt = 0
    for one_data, one_result in zip(data_list, predict_result):

        one_flag = True
        compare_dict = {}
        print(all_cnt,one_data["问题"])
        print(all_cnt,one_data["回答"])

        for one_intent in intent_vocab:

            true_entity = None
            pred_entity = None

            if len(one_data[one_intent]["entities"]):
                true_entity = one_data[one_intent]["entities"][0]

            if one_result[one_intent][1] == 1:
                pred_entity = one_result[one_intent][0]

            compare_dict[one_intent] = [true_entity,pred_entity]
            if true_entity != pred_entity:
                one_flag = False

        if one_flag:
            correct_cnt += 1

        for one_intent, true_pred in compare_dict.items():
            true_entity,pred_entity = true_pred
            if true_entity is not None or pred_entity is not None:
                if_equal = "结果不等" if true_entity != pred_entity else "结果相等"
                print("%d -> %s -> %s -> %s -> %s"%(all_cnt,if_equal,one_intent,true_entity,pred_entity))
                print('-'*50)
        all_cnt += 1
        print("="*100)

    print("data num: %d, correct num: %d"%(N, correct_cnt))
    print("acc: %.4f"%(correct_cnt/N))

if __name__ == "__main__":
    pass
