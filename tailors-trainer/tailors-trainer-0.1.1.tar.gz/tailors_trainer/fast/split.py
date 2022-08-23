# -*- coding: utf-8 -*-
import collections
import json
import os
import random

import hao
from hao.namespaces import attr, from_args
from tailors.fast.tokenizer import JiebaTokenizer
from tqdm import tqdm

LOGGER = hao.logs.get_logger()


@from_args
class Conf(object):
    cut: int = attr(int, required=True, help='size of train + val')
    seed: int = attr(int)
    random: bool = attr(bool, action='store_true')
    ratio: float = attr(float, default=0.8, help='train set ratio')


def process():
    print('[process]')
    conf = Conf()
    LOGGER.info(conf)

    corpus_path = hao.paths.get('data/corpus/raw.jsonl')
    train_path = hao.paths.get('data/corpus/fast/train.txt')
    val_path = hao.paths.get('data/corpus/fast/val.txt')

    lines = open(corpus_path).readlines()
    entries = [json.loads(line) for line in lines if len(line.strip()) > 0]
    entries_general = entries[:conf.cut]
    entries_extra = entries[conf.cut:]

    if conf.seed:
        random.seed(conf.seed)
        random.shuffle(entries_general)
    elif conf.random:
        seed = random.randint(0, 10000)
        LOGGER.info(f"[seed] using random seed: {seed}")
        random.seed(seed)
        random.shuffle(entries_general)

    i = int(conf.ratio * len(entries_general))
    entries_train = entries_general[:i] + entries_extra
    entries_val = entries_general[i:]

    tokenizer = JiebaTokenizer()
    save_to_file(tokenizer, train_path, entries_train)
    save_to_file(tokenizer, val_path, entries_val)


def save_to_file(tokenizer: JiebaTokenizer, file_path: str, entries: list):
    counter = collections.Counter()
    hao.paths.make_parent_dirs(file_path)
    with open(file_path, "w") as f:
        for entry in tqdm(entries, desc=os.path.basename(file_path)):
            counter.update((entry.get('label'),))
            line = f"{tokenizer.cut_and_join(entry.get('text'))} __label__{entry.get('label')}\n"
            f.write(line)
    for label, count in counter.items():
        LOGGER.info(f"{label: >10}: {count}")
    LOGGER.info(f"saved {len(entries)} lines to {file_path}")


if __name__ == '__main__':
    try:
        process()
    except KeyboardInterrupt:
        print('[ctrl-c] stopped')
    except Exception as err:
        LOGGER.exception(err)
