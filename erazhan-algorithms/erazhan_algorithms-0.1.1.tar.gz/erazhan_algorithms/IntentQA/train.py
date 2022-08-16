# -*- coding = utf-8 -*-
# @time: 2022/3/7 3:22 下午
# @Author: erazhan
# @File: train.py

# ----------------------------------------------------------------------------------------------------------------------
import os
from transformers import BertTokenizer
from tqdm import tqdm, trange

import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from torch.optim import Optimizer,Adam,SGD,Adagrad

from erazhan_algorithms.TC.train import warmup_linear

from .data import convert_to_inputdata_intentqa, trans_inputdata_intentqa
from .models import init_intentqa_model
from .predict import eval_intentqa

def train_intentqa(**kwargs):

    required_params = ["args", "train_data", "eval_data"]
    for one_param in required_params:
        assert one_param in kwargs, "%s not in kwargs" % (one_param)

    # 参数在函数外提供
    args = kwargs["args"]

    train_data_list = kwargs["train_data"]
    eval_data_list = kwargs["eval_data"]

    intent_vocab = args.intent_vocab
    # num_intents = args.num_intents

    tokenizer = kwargs["tokenizer"] if "tokenizer" not in kwargs.keys() else BertTokenizer.from_pretrained(args.bert_model)

    train_InputData_list = convert_to_inputdata_intentqa(tokenizer, train_data_list,intent_vocab, maxlen=args.maxlen, mode="train", disable=args.disable)
    eval_InputData_list = convert_to_inputdata_intentqa(tokenizer, eval_data_list,intent_vocab, maxlen=args.maxlen, mode="train", disable=args.disable)

    print("len(train_InputData_list):", len(train_InputData_list))
    print("len(eval_InputData_list):", len(eval_InputData_list))

    model = init_intentqa_model(args)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # optimizer
    optimizer = Adam(model.parameters(), lr=args.learning_rate)

    all_input_ids, all_input_masks, all_segment_ids, all_intent_labels, all_start_labels, all_end_labels = trans_inputdata_intentqa(train_InputData_list, mode="train")

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)
    all_segment_ids = torch.tensor(all_segment_ids, dtype=torch.long).to(device)

    all_intent_labels = torch.tensor(all_intent_labels, dtype=torch.long).to(device)
    all_start_labels = torch.tensor(all_start_labels, dtype=torch.long).to(device)
    all_end_labels = torch.tensor(all_end_labels, dtype=torch.long).to(device)

    train_data = TensorDataset(all_input_ids, all_input_masks, all_segment_ids, all_intent_labels, all_start_labels, all_end_labels)

    train_sampler = RandomSampler(train_data)
    train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=args.batch_size)

    # train
    model.train()
    global_step = 0
    num_train_steps = args.epochs * len(all_input_ids) / args.batch_size

    for _ in trange(int(args.epochs), desc = "intentqa train epoch", disable = args.disable):

        for step, batch in enumerate(tqdm(train_dataloader, desc = "intentqa train batch",disable = args.disable)):

            input_ids, input_mask, segment_ids, intent_labels, start_position_labels, end_position_labels  = batch

            intent_logits, start_end_logits, intent_loss, position_loss= model(input_ids = input_ids,
                                                                             attention_mask=input_mask,
                                                                             token_type_ids=segment_ids,
                                                                             intent_labels = intent_labels,
                                                                             start_position_labels = start_position_labels, # 将位置向量合并在一起
                                                                             end_position_labels = end_position_labels,
                                                                             )

            loss = intent_loss + position_loss if position_loss is not None else intent_loss
            loss.backward()

            lr_this_step = args.learning_rate * warmup_linear(global_step / num_train_steps, args.warmup_proportion)
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr_this_step
            optimizer.step()
            optimizer.zero_grad()
            global_step += 1

            if global_step % args.print_steps == 0:
                print("global_step:", global_step, "loss:", loss.detach().cpu().numpy(),"intent_loss:",intent_loss.detach().cpu().numpy(),"position_loss:",position_loss.detach().cpu().numpy() if position_loss is not None else None)

            if global_step % args.save_steps == 0:
                model_to_save = model.module if hasattr(model, 'module') else model  # Only save the model it-self

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

    model.eval()
    eval_intentqa(model,eval_data_list,**kwargs)

if __name__ == "__main__":
    pass
