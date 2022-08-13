""" cloze """
from wenxin_api.api import Task
from wenxin_api.error import MissingRequestArgumentError

class Cloze(Task):
    """ cloze task """
    @classmethod
    def create(cls, *args, **params):
        """ create """
        params["seq_len"] = params.get("seq_len", 512)
        params["topp"] = params.get("topp", 0.9)
        params["penalty_score"] = params.get("penalty_score", 1.0)
        params["is_unidirectional"] = params.get("is_unidirectional", 0)
        params["min_dec_len"] = params.get("min_dec_len", 1)
        params["task_prompt"] = params.get("task_prompt", "cloze")
        if "text" not in params:
            raise MissingRequestArgumentError("text must exists in parmas dict")
        params["text"] = params["text"].replace("_", "[MASK]")
        resp = super().create(*args, **params)
        return resp
