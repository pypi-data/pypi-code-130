# -*- coding = utf-8 -*-
# @time: 2022/3/3 6:32 下午
# @Author: erazhan
# @File: train.py

# ----------------------------------------------------------------------------------------------------------------------

import os
from transformers import BertTokenizer
from tqdm import tqdm, trange

import torch
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from torch.optim import Optimizer,Adam,SGD,Adagrad

from erazhan_algorithms.TC.train import warmup_linear

from .data import convert_to_inputdata_qa, trans_inputdata_qa
from .models import init_qa_model

def train_qa(**kwargs):

    required_params = ["args", "train_data", "eval_data"]
    for one_param in required_params:
        assert one_param in kwargs, "%s not in kwargs"%(one_param)

    # 参数在函数外提供
    args = kwargs["args"]

    train_data_list = kwargs["train_data"]
    eval_data_list = kwargs["eval_data"]

    tokenizer = kwargs["tokenizer"] if "tokenizer" not in kwargs.keys() else BertTokenizer.from_pretrained(args.bert_model)
    train_InputData_list = convert_to_inputdata_qa(tokenizer, train_data_list, maxlen = args.maxlen, mode = "train", disable=args.disable, doc_token = args.doc_token)
    eval_InputData_list = convert_to_inputdata_qa(tokenizer,eval_data_list, maxlen = args.maxlen, mode = "train",disable = args.disable, doc_token = args.doc_token)

    print("len(train_InputData_list):",len(train_InputData_list))
    print("len(eval_InputData_list):", len(eval_InputData_list))

    model = init_qa_model(args)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # optimizer
    optimizer = Adam(model.parameters(), lr = args.learning_rate)
    # optimizer = AdamW()

    # train
    all_input_ids, all_input_masks, all_segment_ids, all_start_position_labels, all_end_position_labels = trans_inputdata_qa(train_InputData_list, mode = "train", disable = args.disable)

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)
    all_segment_ids = torch.tensor(all_segment_ids, dtype=torch.long).to(device)

    all_start_position_labels = torch.tensor(all_start_position_labels, dtype=torch.long).to(device)
    all_end_position_labels = torch.tensor(all_end_position_labels, dtype=torch.long).to(device)

    train_data = TensorDataset(all_input_ids, all_input_masks, all_segment_ids, all_start_position_labels, all_end_position_labels)
    train_sampler = RandomSampler(train_data)
    train_dataloader = DataLoader(train_data, sampler = train_sampler, batch_size = args.batch_size)

    model.train()
    global_step = 0
    num_train_steps = args.epochs * len(all_input_ids) / args.batch_size

    for _ in trange(int(args.epochs), desc = "qa train epoch", disable = args.disable):

        for step, batch in enumerate(tqdm(train_dataloader, desc = "qa train batch",disable = args.disable)):

            input_ids, input_mask, segment_ids, start_position_labels, end_position_labels = batch

            loss = model(input_ids=input_ids,
                         attention_mask=input_mask,
                         token_type_ids=segment_ids,
                         start_position_labels=start_position_labels,
                         end_position_labels=end_position_labels)
            if loss is None:
                continue
            loss.backward()

            lr_this_step = args.learning_rate * warmup_linear(global_step / num_train_steps, args.warmup_proportion)
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr_this_step
            optimizer.step()
            optimizer.zero_grad()
            global_step += 1

            if global_step % args.print_steps == 0:
                print("global_step:", global_step, "loss:", loss.detach().cpu().numpy())

            if global_step % args.save_steps == 0:

                # save model every 500 steps
                model_to_save = model.module if hasattr(model, 'module') else model

                if not os.path.exists(args.output_dir):
                    os.mkdir(args.output_dir)

                output_model_file = os.path.join(args.output_dir, "pytorch_model.bin")
                torch.save(model_to_save.state_dict(), output_model_file)

    # save model
    model_to_save = model.module if hasattr(model, 'module') else model

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    output_model_file = os.path.join(args.output_dir, "pytorch_model.bin")
    torch.save(model_to_save.state_dict(), output_model_file)

    # eval
    all_input_ids, all_input_masks, all_segment_ids, all_start_position_labels, all_end_position_labels = trans_inputdata_qa(eval_InputData_list, mode="eval", disable=args.disable)

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)
    all_segment_ids = torch.tensor(all_segment_ids, dtype=torch.long).to(device)

    eval_data = TensorDataset(all_input_ids, all_input_masks, all_segment_ids)
    eval_sampler = SequentialSampler(eval_data)
    eval_dataloader = DataLoader(eval_data, sampler=eval_sampler,
                                 batch_size=args.predict_batch_size)

    model.eval()

    start_target_list = []
    end_target_list = []

    for input_ids, input_mask, segment_ids in tqdm(eval_dataloader, desc='qa eval batch'):
        input_ids = input_ids.to(device)
        input_mask = input_mask.to(device)
        segment_ids = segment_ids.to(device)

        with torch.no_grad():
            # [bsz, maxlen], [bsz, maxlen]
            start_logits, end_logits = model(input_ids=input_ids, attention_mask=input_mask, token_type_ids=segment_ids)

            start_logits = F.softmax(start_logits.detach().cpu(), dim=1) # [bsz,maxlen]
            start_result = torch.max(start_logits, dim=1, keepdims=False)
            start_pred_target = start_result.indices.tolist()
            start_target_list.extend(start_pred_target)

            end_logits = F.softmax(end_logits.detach().cpu(), dim=1)
            end_result = torch.max(end_logits, dim=1, keepdims=False)
            end_pred_target = end_result.indices.tolist()
            end_target_list.extend(end_pred_target)

    N = len(all_start_position_labels)

    print("start true and predict first 100:\n %s \n %s"%(all_start_position_labels[:100], start_target_list[:100]))
    print("end true and predict first 100 :\n %s \n %s" % (all_end_position_labels[:100], end_target_list[:100]))

    correct = 0

    for i in range(N):

        true_start = all_start_position_labels[i]
        true_end = all_end_position_labels[i]

        predict_start = start_target_list[i]
        predict_end = end_target_list[i]

        if true_start==predict_start and true_end == predict_end:
            correct += 1

    print("Accuracy:", correct / N)

if __name__ == "__main__":
    pass
