# -*- coding: utf-8 -*-
import torch
from decorator import decorator


def freeze(model):
    for param in model.parameters():
        param.requires_grad = False


def unfreeze(model):
    for param in model.parameters():
        param.requires_grad = True


def init(model):
    for layer in model.modules():
        if isinstance(layer, torch.nn.Conv2d):
            torch.nn.init.kaiming_normal_(layer.weight, mode='fan_out', nonlinearity='relu')
            if layer.bias is not None:
                torch.nn.init.constant_(layer.bias, val=0.0)

        elif isinstance(layer, torch.nn.BatchNorm2d):
            torch.nn.init.constant_(layer.weight, val=1.0)
            torch.nn.init.constant_(layer.bias, val=0.0)

        elif isinstance(layer, torch.nn.Linear):
            torch.nn.init.xavier_normal_(layer.weight)
            if layer.bias is not None:
                torch.nn.init.constant_(layer.bias, val=0.0)


def move_to_device(data, device, non_blocking=True):
    if device is None:
        return
    if isinstance(data, dict):
        return {k: move_to_device(v, device, non_blocking) for k, v in data.items()}
    elif isinstance(data, tuple):
        return tuple([move_to_device(v, device, non_blocking) for v in data])
    elif isinstance(data, list):
        return [move_to_device(v, device, non_blocking) for v in data]
    elif isinstance(data, torch.Tensor):
        return data.to(device, non_blocking=non_blocking)
    return data


@decorator
def auto_device(func, *a, **kw):
    def wrapper(self, *args, **kwargs):
        args = move_to_device(args, self.device)
        kwargs = move_to_device(kwargs, self.device)
        return func(self, *args, **kwargs)
    return wrapper(*a, **kw)
