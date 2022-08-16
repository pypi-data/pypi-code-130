# -*- coding:utf-8 -*-
# @time: 2022/6/28 4:44 下午
# @Author: erazhan
# @File: models.py

# ----------------------------------------------------------------------------------------------------------------------
import os
import torch
from torch import nn
from transformers import BertPreTrainedModel, BertModel
# from torchcrf import CRF # 好像需要0.4.0版本
from torch.nn import CrossEntropyLoss

class Bert4NER(BertPreTrainedModel):

    def __init__(self, config):
        super().__init__(config)

        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

        # self.intent_labels = config.num_labels
        self.num_tags = config.num_labels

        # 识别疾病 + 症状 + 角色
        self.tag_classifier = nn.Linear(config.hidden_size, self.num_tags)#,bias = True)
        self.loss_fct = CrossEntropyLoss()

        self.init_weights()

    def forward(self,
                input_ids=None,
                attention_mask = None,
                token_type_ids = None,
                position_ids = None,
                head_mask = None,
                inputs_embeds = None,
                output_attentions = None,
                output_hidden_states = None,
                return_dict = None,
                # intent_labels = None, # 意图标签
                tag_labels = None, # ner标签
                ):
        outputs = self.bert(input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                            position_ids=position_ids,
                            head_mask=head_mask,
                            inputs_embeds=inputs_embeds,  # 有版本后面是不执行的
                            output_attentions=output_attentions,
                            output_hidden_states=output_hidden_states,
                            return_dict=return_dict, )

        sequence_output = outputs[0] # [batch_size,max_length,hidden_size]
        # cls_out = outputs[1] # [batch_size,hidden_size]

        sequence_output = self.dropout(sequence_output)
        # cls_out = self.dropout(cls_out)

        tag_logits = self.tag_classifier(sequence_output)

        # intent_logits = self.intent_classifier(cls_out)
        # outputs = (intent_logits,tag_logits,site_tag_logits)
        outputs = (tag_logits,)

        loss = None

        if tag_labels is not None:

            active_tag_loss = attention_mask.view(-1) == 1
            active_tag_logits = tag_logits.view(-1, self.num_tags)[active_tag_loss]
            active_tag_labels = tag_labels.view(-1)[active_tag_loss]
            tag_loss = self.loss_fct(active_tag_logits, active_tag_labels)
            if loss is None:
                loss = tag_loss
            else:
                loss += tag_loss

        if loss is not None:
            return loss

        return outputs

def init_ner_model(args, from_scratch = True):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if from_scratch:
        model = Bert4NER.from_pretrained(args.bert_model, num_labels = args.num_tags)
    else:
        predict_model_file = os.path.join(args.predict_dir, "pytorch_model.bin")
        model_state_dict = torch.load(predict_model_file)
        model = Bert4NER.from_pretrained(args.bert_model, num_labels = args.num_tags, state_dict = model_state_dict)

    model.to(device)

    return model

if __name__ == "__main__":

    pass