# -*- coding: utf-8 -*-
from hao.namespaces import from_args, attr


@from_args
class TaskConf:
    name: str = attr(str, required=True)
    model: str = attr(str, required=True)
    datasets: str = attr(str, required=True)


class Task:

    def __init__(self,
                 name: str,
                 model: str,
                 datasets: str) -> None:
        pass
