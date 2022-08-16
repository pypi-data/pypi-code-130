# -*- coding = utf-8 -*-
# @time: 2022/3/3 6:32 下午
# @Author: erazhan
# @File: utils.py

# ----------------------------------------------------------------------------------------------------------------------

QA_DEFAULT_PARAM_DICT = {"gpu": 0,
                         "maxlen": 256,
                         "batch_size":32,
                         "predict_batch_size":4,
                         "learning_rate":2e-5,
                         "warmup_proportion":0.1,
                         "epochs": 5,
                         "save_steps": 500,
                         "print_steps": 20,
                         "disable": False}

QA_OTHER_PARAM_DICT = {"bert_model": None,
                       "train_file": None,
                       "eval_file": None,
                       "output_dir": None,
                       "predict_dir": None
                       }

class qa_params(object):

    def __init__(self, param_dict):

        for param_name, param_value in param_dict.items():

            if type(param_value) == str:
                exec("self.%s = '%s'" % (param_name, param_value))
                continue

            if type(param_value) in [int,float]:
                param_value = str(param_value)

            exec("self.%s = %s"%(param_name,param_value))

def get_qa_parser(param_dict):

    P = qa_params(param_dict)

    return P

def get_qa_params_help():

    from erazhan_utils import trans2json

    useage_method = """
    import copy
    param_dict = copy.deepcopy(QA_DEFAULT_PARAM_DICT)
    param_dict.update(QA_OTHER_PARAM_DICT)
    args = get_qa_parser(param_dict)
    """

    print("usage method:\n",useage_method)
    print("QA_DEFAULT_PARAM_DICT:\n",trans2json(QA_DEFAULT_PARAM_DICT))
    print("QA_OTHER_PARMA_DICT:\n",trans2json(QA_OTHER_PARAM_DICT))

if __name__ == "__main__":

    import copy
    param_dict = copy.deepcopy(QA_DEFAULT_PARAM_DICT)
    param_dict.update(QA_OTHER_PARAM_DICT)

    args = get_qa_parser(param_dict)

    get_qa_params_help()

    pass