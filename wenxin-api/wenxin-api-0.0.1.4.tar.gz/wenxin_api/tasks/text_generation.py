""" text generation task """
from wenxin_api.api import Task
from wenxin_api.error import MissingRequestArgumentError


class TextGeneration(Task):
    """ text generation task """
    @classmethod
    def create(cls, *args, **params):
        """ create """
        params["seq_len"] = params.get("seq_len", 512)
        params["topp"] = params.get("topp", 0.9)
        params["penalty_score"] = params.get("penalty_score", 1.2)
        params["min_dec_len"] = params.get("min_dec_len", 4)
        params["is_unidirectional"] = params.get("is_unidirectional", 1)
        params["task_prompt"] = params.get("task_prompt", "PARAGRAPH")
        params["penalty_text"] = params.get("penalty_text", "[{[gEND]")
        params["min_dec_penalty_text"] = params.get("min_dec_penalty_text", "。？：！[<S>]")
        params["logits_bias"] = params.get("logits_bias", -10)
        params["mask_type"] = params.get("mask_type", "paragraph")
        resp = super().create(*args, **params)
        return resp