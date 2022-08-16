# -*- coding = utf-8 -*-
# @time: 2022/3/3 5:57 下午
# @Author: erazhan
# @File: models.py

# ----------------------------------------------------------------------------------------------------------------------
import os

from transformers import BertPreTrainedModel,BertModel
import torch
from torch import nn
from torch.nn import CrossEntropyLoss,BCEWithLogitsLoss

# Bert4QA模型
# 例如：query:"身高体重多少?" answer:"身高172cm，体重60kg"
# 1、height tokens: ["[CLS]","身","高","[SEP]"] + [for e in query] + ["[SEP]"] + [for e in answer] + ["[sep]"] -> height_offset: []
# 2、weight tokens: ["[CLS]","体","重","[SEP]"] + [for e in query] + ["[SEP]"] + [for e in answer] + ["[sep]"] -> weight_offset: []

class Bert4QA(BertPreTrainedModel):

    '''专用于问答抽取模型,单段抽取'''

    def __init__(self,config):

        super().__init__(config)
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

        self.qa_outputs = nn.Linear(config.hidden_size, 2)

        self.ce_loss_fct = CrossEntropyLoss()
        self.init_weights()

    def forward(self,
                input_ids=None,
                attention_mask=None,
                token_type_ids=None,
                position_ids=None,
                head_mask=None,
                start_position_labels = None,  # 起点向量合并, [bsz, num_intents]
                end_position_labels = None,  # 终点向量合并, [bsz, num_intents]
                ):

        outputs = self.bert(input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                            position_ids=position_ids,
                            head_mask=head_mask
                            )

        sequence_output = outputs[0]  # [bsz, maxlen, hidden]
        # cls_output = outputs[1]  # [bsz, hidden]

        sequence_output = self.dropout(sequence_output)

        logits = self.qa_outputs(sequence_output)  # [bsz, maxlen, 2]
        start_logits, end_logits = logits.split(1, dim=-1) # [bsz, maxlen, 1], [bsz, maxlen, 1]
        start_logits = start_logits.squeeze(-1) # [bsz, maxlen]
        end_logits = end_logits.squeeze(-1) # [bsz, maxlen]

        if start_position_labels is not None and end_position_labels is not None:

            # start/end_position_labels维度为[bsz,], -1表示当前没有数据, 新版本不考虑, 如果抽取不到数据, 则起始点均指向doc_token(放在cls_token之后)
            position_loss = None
            if torch.sum(start_position_labels != -1) and torch.sum(end_position_labels != -1):

                start_logits = start_logits[start_position_labels != -1]
                end_logits = end_logits[end_position_labels != -1]

                start_position_labels = start_position_labels[start_position_labels != -1]
                end_position_labels = end_position_labels[end_position_labels != -1]

                start_loss = self.ce_loss_fct(start_logits, start_position_labels)
                end_loss = self.ce_loss_fct(end_logits, end_position_labels)
                position_loss = start_loss + end_loss

            return position_loss
        else:
            return start_logits, end_logits

def init_qa_model(args, from_scratch = True):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if from_scratch:
        model = Bert4QA.from_pretrained(args.bert_model)
    else:
        predict_model_file = os.path.join(args.predict_dir, "pytorch_model.bin")
        model_state_dict = torch.load(predict_model_file)
        model = Bert4QA.from_pretrained(args.bert_model, state_dict = model_state_dict)

    model.to(device)

    return model