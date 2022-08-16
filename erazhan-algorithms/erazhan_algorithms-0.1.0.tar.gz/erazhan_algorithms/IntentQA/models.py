# -*- coding = utf-8 -*-
# @time: 2022/3/7 1:45 下午
# @Author: erazhan
# @File: models.py

# ----------------------------------------------------------------------------------------------------------------------
import os

from transformers import BertPreTrainedModel,BertModel
import torch
from torch import nn
from torch.nn import CrossEntropyLoss,BCEWithLogitsLoss

class Bert4IntentQA(BertPreTrainedModel):

    '''此版本：多意图分类 + 指针模型抽取回答'''

    def __init__(self, config, num_intents):

        super().__init__(config)
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

        # self.num_labels = config.num_labels # 给出几个类别
        self.num_intents = num_intents

        for i in range(self.num_intents):
            exec("self.intent_classifier_%d = nn.Linear(config.hidden_size, 2)"%i)  # 多意图分类

        self.qa_outputs = nn.Linear(config.hidden_size, self.num_intents * 2)

        self.ce_loss_fct = CrossEntropyLoss()
        self.init_weights()

    def forward(self,
                input_ids=None,
                attention_mask=None,
                token_type_ids=None,
                position_ids=None,
                head_mask=None,
                intent_labels = None,  # [bsz, num_intents]
                start_position_labels = None,  # 起点向量合并, [bsz, num_intents]
                end_position_labels = None, # 终点向量合并, [bsz, num_intents]
                ):

        outputs = self.bert(input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                            position_ids=position_ids,
                            head_mask=head_mask
                            )

        sequence_output = outputs[0]  # [bsz, maxlen, hidden]
        cls_output = outputs[1]  # [bsz, hidden]

        sequence_output = self.dropout(sequence_output)
        cls_output = self.dropout(cls_output)

        intent_logits = [] # [bsz,2] * self.num_intents
        for i in range(self.num_intents):

            one_classifier = eval("self.intent_classifier_%d"%i)
            one_logits = one_classifier(cls_output)

            intent_logits.append(one_logits)

        # intent_logits = self.intent_classifier(cls_output)  # [bsz, num_intents] 老版本
        outputs = (intent_logits,)

        tag_logits = self.qa_outputs(sequence_output)  # [bsz, maxlen, num_intents * 2]

        start_end_logits = [one_logit.squeeze(-1) for one_logit in tag_logits.split(1, dim=-1)] # [bsz, maxlen] * (self.num_intents * 2)

        outputs += (start_end_logits,)

        # intent_labels.shape = [bsz, num_intents]

        if intent_labels is not None or start_position_labels is not None or end_position_labels is not None:

            intent_loss = None
            position_loss = None

            # 单起始点 [bsz, num_intents] -> [bsz,] * num_intents
            split_start_position_labels = [one_label.squeeze(-1) for one_label in start_position_labels.split(1, dim = -1)]
            split_end_position_labels = [one_label.squeeze(-1) for one_label in end_position_labels.split(1, dim = -1)]

            for i in range(self.num_intents):

                one_intent_logit = intent_logits[i] # [bsz, 2]
                one_intent_label = intent_labels[:,i] # [bsz, ]
                tem_intent_loss = self.ce_loss_fct(one_intent_logit, one_intent_label)
                intent_loss = intent_loss + tem_intent_loss if intent_loss is not None else tem_intent_loss

                one_start_logit = start_end_logits[i] # [bsz, maxlen]
                one_end_logit = start_end_logits[i+1] # [bsz, maxlen]

                one_start_label = split_start_position_labels[i] # [bsz, ]
                one_end_label = split_end_position_labels[i] # [bsz, ]

                if torch.sum(one_start_label!=-1) and torch.sum(one_end_label!=-1):

                    one_start_logit = one_start_logit[one_start_label != -1]
                    one_end_logit = one_end_logit[one_end_label != -1]

                    one_start_label = one_start_label[one_start_label != -1]
                    one_end_label = one_end_label[one_end_label != -1]

                    start_loss = self.ce_loss_fct(one_start_logit, one_start_label)
                    end_loss = self.ce_loss_fct(one_end_logit, one_end_label)

                    position_loss = position_loss + start_loss + end_loss if position_loss is not None else start_loss + end_loss

            outputs += (intent_loss,)
            outputs += (position_loss,)

        return outputs

def init_intentqa_model(args, from_scratch = True):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if from_scratch:
        model = Bert4IntentQA.from_pretrained(args.bert_model, num_intents = args.num_intents)
    else:
        predict_model_file = os.path.join(args.predict_dir, "pytorch_model.bin")
        model_state_dict = torch.load(predict_model_file)
        model = Bert4IntentQA.from_pretrained(args.bert_model, num_intents = args.num_intents, state_dict = model_state_dict)

    model.to(device)

    return model