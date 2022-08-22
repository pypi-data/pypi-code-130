import functools
import hashlib
import inspect
import logging
import re
from pathlib import Path
from typing import Dict

from joblib import Parallel, delayed

from src.lwdp.cache import Cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class _Stage:

    @property
    def _src_bytes(self) -> bytes:
        """ Returns the bytestring of this stage's function's code"""
        raw_src = inspect.getsource(self.function)
        no_whitespace_src = raw_src.replace('\n', '').replace(' ', '')
        no_docstring_src = re.sub(re.compile(r'""".*"""'), '', no_whitespace_src)
        return no_docstring_src.encode()

    @property
    def _single_stage_hash(self):
        """ Returns the MD5 hash of this stage's function's code, plus any raw ancestors.
        MD5 is an arbitrary choice, we are only using hashlib to allow updates of the hash"""
        h = hashlib.md5()
        h.update(self._src_bytes)
        # TODO (NP) - ideally we could use the *content* of the data to hash this stage, not just the fname
        raw_ancestors = [v.encode() for v in self.raw_ancestors.values()]
        for raw_ancestor in raw_ancestors:
            h.update(raw_ancestor)
        return h

    @property
    def hash(self):
        """ Returns this stage's hash, hashed with all ancestors """
        h = self._single_stage_hash
        ancestor_code_hashes = [self.stage_ancestors[k].hash for k in
                                sorted(self.stage_ancestors.keys())]
        for ancestor_hash in ancestor_code_hashes:
            h.update(ancestor_hash.hexdigest().encode())
        return h

    @property
    def hash_path(self) -> Path:
        """ The string hexdigest of the current hash plus all ancestor nodes"""
        return Path(self.hash.hexdigest())

    def __init__(self, function, **kwargs):
        self.function = function
        self.cache = None
        if kwargs.pop('cache', None):
            self.cache = Cache()
        self.raw_ancestors: Dict[str, str] = {k: v for k, v in kwargs.items() if isinstance(v, str)}

        # get all ancestor stages
        self.stage_ancestors: Dict[str, _Stage] = {k: v for k, v in kwargs.items() if isinstance(v, _Stage)}

    def __call__(self, *args):
        def _paralleL_call(k, v):
            return k, v()

        def _compute_stage():
            ancestry = Parallel(n_jobs=4)(delayed(_paralleL_call)(k, v) for k, v in self.stage_ancestors.items())
            return self.function(*args, **self.raw_ancestors, **{i[0]: i[1] for i in ancestry})

        current_func_name = self.function.__name__
        if self.cache is not None:
            logger.info(f"Attempting cache read {self.hash_path} for {current_func_name}")
            result = self.cache.read(self.hash_path)
            if result is None:
                logger.info(f"Cache miss for {self.hash_path}, running stage {current_func_name}")
                result = _compute_stage()
                logger.info(f"Stage {current_func_name} run, writing cache to {self.hash_path}")
                self.cache.write(result, self.hash_path)
            return result
        logger.info(f"Running non-cached stage {current_func_name}")
        return _compute_stage()


def stage(function=None, **kwargs):
    if function:
        return _Stage(function)
    else:
        @functools.wraps(function)
        def wrapper(function):
            return _Stage(function, **kwargs)

        return wrapper
