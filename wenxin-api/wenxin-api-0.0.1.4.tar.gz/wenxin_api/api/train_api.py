# !/usr/bin/env python3
""" train api """
import json
from wenxin_api import requestor, error
from wenxin_api.api import CreatableAPIObject, ListableAPIObject, StopableAPIObject, RetrievalableAPIObject
from wenxin_api.base_object import BaseObject
from wenxin_api.const import CMD_DO_TRAIN, CMD_QUERY_TASK, CMD_STOP_TASK
from wenxin_api.const import TRAIN_TASK
from wenxin_api.error import MissingRequestArgumentError, IlleagalRequestArgumentError

class Train(ListableAPIObject, CreatableAPIObject, StopableAPIObject, RetrievalableAPIObject):
    OBJECT_NAME = "fine-tunes"

    @classmethod
    def create(cls, train_datasets:list=[], dev_datasets:list=[], **params):
        print("create input:", train_datasets, "other params:", params)
        if len(train_datasets) == 0:
            raise IlleagalRequestArgumentError("train datasets shouldn't be null")

        train_data_ids = [dataset.id for dataset in train_datasets]
        if len(dev_datasets) > 0:
            dev_data_ids = [dataset.id for dataset in dev_datasets]
        else:
            dev_data_ids = []

        request_id = CMD_DO_TRAIN
        params["type"] = "task"
        resp = super().create(request_id=request_id, 
                              train_data_ids=train_data_ids, 
                              dev_data_ids=dev_data_ids, 
                              **params)
        return resp

    @classmethod
    def list(cls, *args, **params):
        """ list """
        request_id = CMD_QUERY_TASK
        params["type"] = "task"
        resps = super().list(request_id=request_id, **params)
        filtered_resps = [resp for resp in resps \
                            if resp.status >= 200 and \
                               resp.status < 300]
        return filtered_resps

    @classmethod
    def retrieve(cls, *args, **params):
        """ retrieve """
        request_id = CMD_QUERY_TASK
        params["type"] = "task"
        resp = super().retrieve(request_id=request_id, **params)
        return resp

    @classmethod
    def stop(cls, *args, **params) -> BaseObject:
        request_id = CMD_STOP_TASK
        params["type"] = "task"
        params["task_type"] = TRAIN_TASK
        if isinstance(cls, Train):
            params["task_id"] = cls.id
        if "task_id" not in params:
            raise MissingRequestArgumentError("task_id is not provided")
        return super().stop(request_id=request_id, **params)

    def update(self, *args, **params):
        """ update """
        print("train task is updating now!")
        request_id = CMD_QUERY_TASK
        params["type"] = "task"
        task = super().retrieve(task_id=self.id, request_id=request_id, **params)
        self.refresh_from(task)

    def __str__(self):
        return "Task {}:{}\n".format(
                        id(self),
                        json.dumps({"id": self.id, 
                                    "status": self.status,
                                    "base_model": self.base_model,
                                    "job_id": self.job_id,
                                    "type": self.type
                                   }, ensure_ascii=False)
        )

    def __repr__(self):
        return self.__str__()

