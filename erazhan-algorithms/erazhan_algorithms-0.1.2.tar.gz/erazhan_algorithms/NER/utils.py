# -*- coding:utf-8 -*-
# @time: 2022/6/28 4:45 下午
# @Author: erazhan
# @File: utils.py

# ----------------------------------------------------------------------------------------------------------------------
NER_DEFAULT_PARAM_DICT = {"gpu": 2,
                         "maxlen": 256,
                         "batch_size":32,
                         "predict_batch_size":4,
                         "learning_rate":2e-5,
                         "warmup_proportion":0.1,
                         "epochs": 1,
                         "save_steps": 500,
                         "print_steps": 20,
                         "use_dict": False,
                         "disable": False}

NER_OTHER_PARAM_DICT = {"bert_model": None,
                        "train_file": None,
                        "eval_file": None,
                        "output_dir": None,
                        "predict_dir": None,
                        "standard_disease_file":None,
                        "standard_symptom_file":None,
                        "ner_tags": None,
                        "num_tags": None,
                        "ner_tag2id": None,
                        "ner_id2tag": None,
                       }

class ner_params(object):

    def __init__(self, param_dict):

        for param_name, param_value in param_dict.items():

            if type(param_value) == str:
                exec("self.%s = '%s'" % (param_name, param_value))
                continue

            if type(param_value) in [int,float]:
                param_value = str(param_value)

            exec("self.%s = %s"%(param_name,param_value))

def get_ner_parser(param_dict):

    P = ner_params(param_dict)

    return P

def get_norm_dict(symptom_file, disease_file):
    '''
    :return: 识别标准症状库+疾病库+角色库的字典ner
    '''
    import jionlp as jio
    from erazhan_utils import read_txt_file

    symptom_list = read_txt_file(symptom_file)
    disease_list = read_txt_file(disease_file)
    # 重复的按照疾病
    symptom_list = list(set(symptom_list) - (set(symptom_list) & set(disease_list)))

    # D = {"疾病": ["高血压", "肾衰竭", "感冒"]}
    D = {"疾病": disease_list, "症状": symptom_list}
    ner = jio.ner.LexiconNER(D)

    return ner

def is_inter(a, b):
    x = set(range(a[0], a[1]))
    y = set(range(b[0], b[1]))
    return len(x.intersection(y)) > 0

# args = get_ner_parser()
#
# if args.user_dict:
#     ner = get_norm_dict(args)

def search_entity(tokens, tags, rule_ner = None):

    '''
    :param tokens: ['感','冒']
    :param tags: ['B-疾病','I-疾病']
    :param user_dict: 为True时，保留：1、模型+字典识别一致的; 2、模型和规则均识别出，但位置不等只是部分交叉，则以规则为准; 3、模型或规则之一识别出，另一个为识别出的
    实际使用中，user_dict为True(改为rule_ner)时，会破坏模型识别较好的结果，所以暂不考虑
    :return: {'type': '疾病', 'text': '感冒', 'offset': [0, 2]}
    '''

    assert len(tokens) == len(tags)
    model_entity_list = []
    i = 0
    while i < len(tags):

        tag = tags[i]

        if tag.startswith('B'):

            entity_type = tag[2:]
            value = tokens[i]
            start_index = i
            j = i + 1
            while j < len(tags):
                if tags[j].startswith('I') and tags[j][2:] == tag[2:]:

                    if tokens[j].startswith('##'):
                        value += tokens[j][2:]
                    else:
                        value += tokens[j]
                    i += 1
                    j += 1
                else:
                    break
            if len(value) > 1:
                one_entity = {"type": entity_type, "text": value, "offset": [start_index,start_index+len(value)]}
                model_entity_list.append(one_entity)

        elif tag.startswith("S"):
            entity_type = tag[2:]
            value = tokens[i]
            one_entity = {"type":entity_type,"text":value,"offset":[i,i+1]}
            model_entity_list.append(one_entity)

        i += 1

    if rule_ner is not None:

        rule_entity_list = rule_ner(''.join(tokens))

        for model_entity in model_entity_list[:]:

            model_offset = tuple(model_entity['offset'])

            for rule_entity in rule_entity_list:
                rule_offset = tuple(rule_entity['offset'])
                if model_offset == rule_offset:
                    rule_entity_list.remove(rule_entity)
                    break
                else:
                    if is_inter(model_offset,rule_offset):
                        model_entity_list.remove(model_entity)
                        model_entity_list.append(rule_entity)
                        rule_entity_list.remove(rule_entity)
                        break
        if rule_entity_list:
            for rule_entity in rule_entity_list:
                model_entity_list.append(rule_entity)

    model_entity_list = sorted(model_entity_list,key = lambda x:x['offset'][0])

    return model_entity_list

if __name__ == "__main__":

    tokens =['我', '爸', '突', '然', '大', '汗', '，', '还', '有', '糖', '尿', '病', ',', '头', '突', '然', '痛']
    tags = ['O', 'S-角色', 'B-症状', 'I-症状', 'I-症状', 'I-症状', 'O', 'O', 'O', 'B-疾病', 'I-疾病', 'I-疾病', 'O', 'B-症状', 'I-症状', 'I-症状', 'I-症状']
    ans = search_entity(tokens,tags)
    print(ans)
