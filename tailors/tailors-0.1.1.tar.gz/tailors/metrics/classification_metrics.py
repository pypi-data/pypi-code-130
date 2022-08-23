# -*- coding: utf-8 -*-
import functools
from typing import List, Optional

import torch
from sklearn import metrics

precision_score = functools.partial(metrics.precision_score, average='micro', zero_division=0)
recall_score = functools.partial(metrics.recall_score, average='micro', zero_division=0)
f1_score = functools.partial(metrics.f1_score, average='micro', zero_division=0)
classification_report = functools.partial(metrics.classification_report, digits=4, zero_division=0)


def calculate(target, preds, labels: Optional[List[str]] = None):
    targets = target.tolist()
    return {
        'precision': precision_score(targets, preds, labels=labels),
        'recall': recall_score(targets, preds, labels=labels),
        'f1': f1_score(targets, preds, labels=labels),
        'report': classification_report(targets, preds, labels=labels)
    }
