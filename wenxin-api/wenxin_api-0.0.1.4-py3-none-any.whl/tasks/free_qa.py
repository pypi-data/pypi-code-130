""" free qa task """
from wenxin_api.api import Task
from wenxin_api.error import MissingRequestArgumentError


class FreeQA(Task):
    """ free qa task """
    @classmethod
    def create(cls, *args, **params):
        """ create """
        params["seq_len"] = params.get("seq_len", 512)
        params["topp"] = params.get("topp", 0.9)
        params["penalty_score"] = params.get("penalty_score", 1.2)
        params["penalty_text"] = params.get("penalty_text", "[gEND]")
        params["min_dec_len"] = params.get("min_dec_len", 2)
        params["min_dec_penalty_text"] = params.get("min_dec_penalty_text", "。？：！[<S>]")
        params["is_unidirectional"] = params.get("is_unidirectional", 1)
        params["task_prompt"] = params.get("task_prompt", "qa")
        params["mask_type"] = params.get("mask_type", "paragraph")
        params["logits_bias"] = params.get("logits_bias", -5)
        if "text" not in params:
            raise MissingRequestArgumentError("text must exists in parmas dict")
        params["text"] = "问题：{} 回答：".format(params["text"])
        resp =  super().create(*args, **params)
        return resp