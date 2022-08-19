# -*- coding: utf-8 -*-

class TailorsTrainerError(Exception):
    """Raise on issues in config/class/params in train/val/infer loops..."""


class StopTailorsTrainer(TailorsTrainerError):
    """
    Raise on any condition that the train loop should stop.
    e.g. EarlyStop, ...
    """
