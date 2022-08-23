# -*- coding: utf-8 -*-
import datetime
import itertools
import os
import typing

import fasttext
import hao
from hao.namespaces import attr, from_args
from hao.stopwatch import Stopwatch
from sklearn.metrics import classification_report

LOGGER = hao.logs.get_logger(__name__)


PARAM_MAPPING = {
    'train_file': 'input',
    'val_file': 'autotuneValidationFile',
    'tune_time': 'autotuneDuration',
    'tune_size': 'autotuneModelSize',
    'pretrained_file': 'pretrainedVectors',
    'min_count': 'minCount',
    'ngram': 'wordNgrams',
}
FILE_SKIP_ATTR = ('pretrained_file', 'train_file', 'val_file', 'tune_time', 'tune_size')

@from_args
class TrainConf(object):
    exp: str = attr(str, required=True, help='experiment name')
    file_train: str = attr(str, default='data/corpus/fast/train.txt', required=True)
    file_val: str = attr(str, default='data/corpus/fast/val.txt', required=True)
    tune_time: int = attr(int, default=600, help='auto tune duration in seconds')
    tune_size: str = attr(str, default="100M", help='auto tune model size')
    lr: list = attr(typing.List[float], default=[])
    dim: list = attr(typing.List[int], default=[50])
    ws: list = attr(typing.List[int], default=[], help="window size")
    epoch: list = attr(typing.List[int], default=[])
    neg: list = attr(typing.List[int], default=[])
    min_count: list = attr(typing.List[int], default=[30])
    ngram: list = attr(typing.List[int], default=[3])
    minn: list = attr(typing.List[int], default=[])
    maxn: list = attr(typing.List[int], default=[])
    loss: list = attr(typing.List[str], choices=('ns', 'hs', 'softmax', 'ova'), default=[])
    pretrained: str = attr(str)


def train():
    conf = TrainConf()
    LOGGER.info(conf)
    train_file = hao.paths.get(conf.file_train)
    val_file = hao.paths.get(conf.file_val)
    pretrained_file = hao.paths.get(conf.pretrained)

    for lr, dim, epoch, ws, neg, min_count, ngram, minn, maxn, loss in itertools.product(
            conf.lr or [None],
            conf.dim or [None],
            conf.epoch or [None],
            conf.ws or [None],
            conf.neg or [None],
            conf.min_count or [None],
            conf.ngram or [None],
            conf.minn or [None],
            conf.maxn or [None],
            conf.loss or [None]
    ):
        params = {
            'pretrained_file': pretrained_file,
            'train_file': train_file,
            'val_file': val_file,
            'tune_time': conf.tune_time,
            'tune_size': conf.tune_size,
            'lr': lr,
            'dim': dim,
            'epoch': epoch,
            'ws': ws,
            'neg': neg,
            'min_count': min_count,
            'ngram': ngram,
            'minn': minn,
            'maxn': maxn,
            'loss': loss,
        }
        train_and_val(conf.exp, **params)


def train_and_val(exp: str, **kwargs):
    params = {PARAM_MAPPING.get(k, k): v for k, v in kwargs.items() if v}
    LOGGER.info(f'train: \n{hao.jsons.prettify(params)}')

    sw = Stopwatch()
    date = datetime.datetime.now().strftime('%y%m%d-%H%M')
    model = fasttext.train_supervised(**params)
    LOGGER.info(len(model.words))
    LOGGER.info(model.labels)

    file_val = kwargs.get('val_file')
    n, precision, recall = model.test(file_val)
    f1 = 2 * precision * recall / (precision + recall)
    LOGGER.info(f"n: {n}, precision: {precision:.4}, recall: {recall:.4}, f1: {f1:.4}")

    model_params = '-'.join([
        f'{k}={v}' for k, v in kwargs.items()
        if k not in FILE_SKIP_ATTR and v is not None
    ])
    model_name = f'{exp}-{date}-{model_params}-f1={f1:.4}.bin'
    model_path = hao.paths.get('data/model', model_name)
    hao.paths.make_parent_dirs(model_path)
    model.save_model(model_path)

    size = round(os.path.getsize(model_path) / (1024*1024), 2)
    LOGGER.info(f'model saved to: {model_path}, size: {size}')
    for att in ('lr', 'dim', 'epoch', 'ws', 'neg', 'minCount', 'wordNgrams', 'minn', 'maxn'):
        LOGGER.info(f'{att: >25}: {getattr(model, att)}')

    lines = open(file_val).readlines()
    text, labels = list(zip(*[line.split('__label__') for line in lines]))
    preds = [pred[0].strip('__label__') for pred in model.predict(list(text))[0]]
    labels = [label.strip() for label in labels]
    report = classification_report(labels, preds, digits=4, zero_division=0)
    LOGGER.info(f"\n{' classification report '.center(60, '=')}\n{report}")

    LOGGER.info(f'took: {sw.took()}')
    return model_name, f1


if __name__ == '__main__':
    try:
        train()
    except KeyboardInterrupt:
        print('[ctrl-c] stopped')
    except Exception as err:
        LOGGER.exception(err)
