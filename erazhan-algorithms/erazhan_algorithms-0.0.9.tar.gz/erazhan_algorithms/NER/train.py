# -*- coding:utf-8 -*-
# @time: 2022/6/28 4:45 下午
# @Author: erazhan
# @File: train.py

# ----------------------------------------------------------------------------------------------------------------------
import os
from transformers import BertTokenizer
from tqdm import tqdm, trange

import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from torch.optim import Optimizer,Adam,SGD,Adagrad

from data import convert_to_inputdata_ner, trans_inputdata_ner
from models import init_ner_model

from erazhan_algorithms import warmup_linear

def train_ner(**kwargs):

    required_params = ["args", "train_text", "eval_text", "train_tags", "eval_tags"]

    for one_param in required_params:
        assert one_param in kwargs, "%s not in kwargs" % (one_param)

    # 参数在函数外提供
    args = kwargs["args"]
    train_text = kwargs["train_text"]
    eval_text = kwargs["eval_text"]

    train_tags = kwargs["train_tags"]
    eval_tags = kwargs["eval_tags"]

    tag2id = args.ner_tag2id
    maxlen = args.maxlen

    tokenizer = kwargs["tokenizer"] if "tokenizer" not in kwargs.keys() else BertTokenizer.from_pretrained(args.bert_model)

    train_InputData_list = convert_to_inputdata_ner(tokenizer, text_list = train_text, tag_list = train_tags, tag2id = tag2id, maxlen = maxlen, disable=False)
    eval_InputData_list = convert_to_inputdata_ner(tokenizer, text_list = eval_text, tag_list = eval_tags, tag2id = tag2id, maxlen = maxlen, disable=False)

    model = init_ner_model(args, from_scratch = True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    optimizer = Adam(model.parameters(), lr = args.learning_rate)

    # train
    all_input_ids, all_input_masks, all_segment_ids, all_tags = trans_inputdata_ner(train_InputData_list, mode="train",disable=args.disable)

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)
    all_segment_ids = torch.tensor(all_segment_ids, dtype=torch.long).to(device)

    all_tags = torch.tensor(all_tags, dtype=torch.long).to(device)

    train_data = TensorDataset(all_input_ids, all_input_masks, all_segment_ids, all_tags)
    train_sampler = RandomSampler(train_data)
    train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=args.batch_size)

    model.train()
    global_step = 0
    num_train_steps = args.epochs * len(all_input_ids) / args.batch_size

    # if not os.path.exists(args.output_dir):
    #     os.mkdir(args.output_dir)

    for _ in trange(int(args.epochs), desc = "ner train epoch", disable = args.disable):

        for step, batch in enumerate(tqdm(train_dataloader, desc = "ner train batch",disable = args.disable)):

            input_ids, input_mask, segment_ids, tag_labels = batch

            # loss = model(input_ids=input_ids, attention_mask=input_mask, token_type_ids=segment_ids, labels=label)
            loss = model(input_ids=input_ids,
                         attention_mask=input_mask,
                         token_type_ids=segment_ids,
                         tag_labels=tag_labels,
                         )

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

if __name__ == "__main__":
    pass
