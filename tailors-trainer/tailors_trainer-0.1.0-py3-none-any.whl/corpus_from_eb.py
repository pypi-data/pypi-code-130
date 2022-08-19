# -*- coding: utf-8 -*-
import collections
import logging
import os
import random

import demjson3
import hao
from hao.mongo import Mongo
from hao.namespaces import attr, from_args
from hao.stopwatch import Stopwatch
from tailors.fast import texts
from tqdm import tqdm

LOGGER = hao.logs.get_logger(__name__)
hao.logs.update_logger_levels({
    "__main__": logging.INFO,
})


@from_args
class Conf(object):
    name: str = attr(str, default='bbm', help='collection name', required=True)
    total: int = attr(int)


def process():
    LOGGER.info('process')
    sw = Stopwatch()
    conf = Conf()
    LOGGER.info(conf)

    path_train = hao.paths.get(f"data/corpus/bidding/train.json")
    path_val = hao.paths.get(f"data/corpus/bidding/val.json")
    hao.paths.make_parent_dirs(path_train)

    items = []
    col_name = conf.name if conf.name.startswith('task-') else f"task-{conf.name}"
    for data in from_eb(col_name, conf.total):
        items.append(data)

    items_train = [item for item in items if item.get('split') == 'train']
    items_val = [item for item in items if item.get('split') == 'val']
    items_cases = [item for item in items if item.get('split') is None]

    for path, entries in ((path_train, items_train + items_cases * 3), (path_val, items_val)):
        with open(path, 'w') as f:
            name = os.path.basename(path)
            counter = collections.Counter()
            for entry in tqdm(entries, desc=name):
                f.write(f"{hao.jsons.dumps(entry)}\n")
                counter.update((entry.get('label'),))
            LOGGER.info(f" {name} ".center(50, '='))
            for label, count in counter.items():
                LOGGER.info(f"{label: <20}: {count}")

    LOGGER.info(f'done, took: {sw.took()}')


def from_eb(col_name: str, size: int):
    LOGGER.info(f"[from eb] {col_name}")
    if size == 0:
        return
    mongo = Mongo()
    query = {'enabled': {'$ne': False}, 'editor_timestamp': {'$ne': None}}

    total = mongo.count(col_name, query)
    if size is not None:
        total = min(size, total)
    count = 0
    for item in tqdm(mongo.find(col_name, query), total=total, desc=f"[{col_name}]"):
        _id = item.get('es_id')
        caption = item.get('caption')
        label = item.get('annotation').get('SLC')
        split = item.get('split')
        text = texts.fix_text(convert_caption(caption))
        if texts.is_invalid_text(text):
            continue
        yield {'_id': _id, 'text': text, 'label': label, 'split': split}
        count += 1
        if count >= total:
            break


def convert_caption(caption: str):
    lines = caption.splitlines()
    products_line, title_line = lines[5], ''.join(lines[6:])
    products = demjson3.decode(products_line[products_line.find('['):])
    title = title_line[title_line.find('标题：') + 3:]
    return f"{'; '.join(products)}; {texts.normalized_title(title)}"
    # return f"{texts.normalized_title(title)}; {'; '.join(products)}"


if __name__ == '__main__':
    try:
        process()
    except KeyboardInterrupt:
        print('[ctrl-c] stopped')
    except Exception as e:
        LOGGER.exception(e)
