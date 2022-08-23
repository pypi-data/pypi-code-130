# -*- coding: utf-8 -*-
import abc
import os
import pickle
from typing import List, Optional

import hao
import lmdb
import rocksdb3
from hao.namespaces import attr, from_args
from hao.singleton import Singleton
from tailors.domains import Derivable
from tailors.models import TailorsIO
from torch.utils.data import Dataset
from torch.utils.data.dataloader import DataLoader
from tqdm import tqdm

from tailors_trainer.exceptions import TailorsTrainerError

LOGGER = hao.logs.get_logger(__name__)


class CacheStore(abc.ABC, Derivable):

    @staticmethod
    def get_instance(name, cache_dir, split) -> 'CacheStore':
        for clz in CacheStore.subclasses():
            if clz.name() == name:
                return clz(cache_dir, split)
        raise TailorsTrainerError(f"Unsupported cache type: {name}")

    def __init__(self, cache_dir: str, split: str) -> None:
        self.path = hao.paths.get(f"data/cache/{cache_dir}/{split}.{self.name()}")
        hao.paths.make_parent_dirs(self.path)
        self.db: Optional[lmdb.Environment] = None
        self.length = -1
        self.keys = None

    @staticmethod
    @abc.abstractmethod
    def name():
        raise NotImplementedError()

    def is_cached(self):
        return os.path.exists(self.path)

    @abc.abstractmethod
    def populate(self, items):
        raise NotImplementedError()

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get(self, index):
        raise NotImplementedError()

    @abc.abstractmethod
    def size(self) -> int:
        raise NotImplementedError()


class NoCacheStore(CacheStore):
    def __init__(self, dir: str, split: str) -> None:
        super().__init__(dir, split)
        self.path = None
        self.items = None

    @staticmethod
    def name():
        return 'no'

    def is_cached(self):
        return self.items is not None

    def load(self):
        pass

    def populate(self, items):
        self.items = list(items)

    def get(self, index):
        return self.items[index]

    def size(self):
        return len(self.items)


class LmdbCacheStore(CacheStore):

    @staticmethod
    def name():
        return 'lmdb'

    def populate(self, items):
        with self.open(readonly=False) as db:
            txn = db.begin(write=True)
            for i, item in enumerate(items):
                txn.put(f"{i}".encode("ascii"), pickle.dumps(item))
                if i % 1001 == 0:
                    txn.commit()
                    txn = db.begin(write=True)
            txn.commit()

    def load(self):
        if self.db is None:
            self.db = self.open()
        with self.db.begin(write=False) as txn:
            self.length = txn.stat()["entries"]
            self.keys = [key for key, _ in txn.cursor()]

    def get(self, index: int):
        with self.db.begin(write=False) as txn:
            return pickle.loads(txn.get(self.keys[index]))

    def open(self, readonly: bool = True) -> lmdb.Environment:
        return lmdb.open(
            self.path,
            subdir=False,
            readonly=readonly,
            lock=not readonly,
            readahead=False,
            meminit=False,
            map_size=1099511627776 * 2,
            map_async=True
        )

    def size(self):
        return self.length


class RocksdbCacheStore(CacheStore):

    @staticmethod
    def name():
        return 'rocksdb'

    def populate(self, items):
        db = rocksdb3.open_default(self.path)
        total = 0
        for i, item in enumerate(items):
            db.put(f"{i}".encode('ascii'), pickle.dumps(item))
            total += 1
        db.put('total'.encode('ascii'), pickle.dumps(total))

    def load(self):
        self.db = rocksdb3.open_default(self.path)
        self.length = self.get('total')

    def get(self, key):
        return pickle.loads(self.db.get(f"{key}".encode('ascii')))

    def size(self):
        return self.length


def cache_names() -> tuple:
    return tuple([clz.name() for clz in CacheStore.subclasses()])


@from_args
class DatasetConf(metaclass=Singleton):
    shuffle: bool = attr(bool, default=True)
    drop_last: bool = attr(bool, default=True)
    bz = attr(int, default=128)
    pin_mem: bool = attr(bool, default=True)
    n_workers = attr(int, default=0)
    cache = attr(str, choices=cache_names(), default=NoCacheStore.name())


class TailorDataset(Dataset):
    def __init__(self, io: TailorsIO, name: str, split: str, files: List[str], dataset_conf: DatasetConf) -> None:
        super().__init__()
        self.io = io
        self.name = name
        self.split = split
        self.files = files if isinstance(files, list) else [files]
        self.dataset_conf = dataset_conf
        self.cache = CacheStore.get_instance(dataset_conf.cache, f"{self.io.__module__}/{self.name}", self.split)

    def load(self):
        if not self.cache.is_cached():
            self.cache.populate(self.from_files())
        self.cache.load()
        LOGGER.info(f"[{self.split}] size: {self.cache.size()}, cache: {self.cache.path or 'n/a'}")
        return self

    def from_files(self):
        for file in self.files:
            yield from self.from_file(file)

    def from_file(self, file):
        file = hao.paths.get(file)
        if not os.path.exists(file):
            raise TailorsTrainerError(f"[dataset] file not found: {file}")
        n_lines = hao.files.count_lines(file)
        with open(file, "r") as f:
            for line in tqdm(f, total=n_lines, desc=f"[dataset] {os.path.basename(file): <20}", ascii='░▒▓', colour='cyan'):
                line = hao.strings.strip_to_none(line)
                if line is None:
                    continue
                items = self.from_line(line)
                for item in items:
                    yield item

    def from_line(self, line: str):
        return self.io.from_line(line)

    def __getitem__(self, index: int):
        return self.cache.get(index)

    def __len__(self) -> int:
        return self.cache.size()

    def dataloader(self):
        return DataLoader(
            self.load(),
            batch_size=self.dataset_conf.bz,
            num_workers=self.dataset_conf.n_workers,
            pin_memory=self.dataset_conf.pin_mem,
            drop_last=self.dataset_conf.drop_last,
            shuffle=self.dataset_conf.shuffle,
            collate_fn=self.io.collate,
        )
