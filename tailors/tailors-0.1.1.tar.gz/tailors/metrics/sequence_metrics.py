# -*- coding: utf-8 -*-
import functools

import torch
from seqeval import metrics

precision_score = functools.partial(metrics.precision_score, average='micro', zero_division=0)
recall_score = functools.partial(metrics.recall_score, average='micro', zero_division=0)
f1_score = functools.partial(metrics.f1_score, average='micro', zero_division=0)
classification_report = functools.partial(metrics.classification_report, digits=4, zero_division=0)


def calculate(target_tags, preds_tags):
    return {
        'precision': precision_score(target_tags, preds_tags),
        'recall': recall_score(target_tags, preds_tags),
        'f1': f1_score(target_tags, preds_tags),
        'report': classification_report(target_tags, preds_tags)
    }
