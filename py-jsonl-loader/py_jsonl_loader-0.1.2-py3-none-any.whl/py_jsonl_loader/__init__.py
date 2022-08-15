import glob
from loguru import logger
import hashlib
import os
from sys import platform
import json
from functools import lru_cache

class JsonLineLoader():
    def __init__(self,dir_or_file,search_sub_dir=True):
        self.length = None
        self.cache = {}

        if os.path.isdir(dir_or_file) and search_sub_dir:
            self.files = glob.glob(os.path.join(dir_or_file,"**","*.jsonl"))
        elif os.path.isdir(dir_or_file) and not search_sub_dir:
            self.files = glob.glob(os.path.join(dir_or_file,"*.jsonl"))
        elif os.path.isfile(dir_or_file):
            self.files = [dir_or_file]
        else:
            assert False
            
        assert len(self.files)>0
        self.files = sorted(self.files)
        logger.info(f"{len(self.files)} files detect")

        # create_hash
        hash_string = ' '.join(self.files).encode()
        hash_string = hashlib.sha1(hash_string).hexdigest()
        
        os.makedirs(os.path.join(os.getcwd(),'.pjl_cache'),exist_ok=True)
        self.cache_path = os.path.join(os.getcwd(),'.pjl_cache',f".pjl_cache.{hash_string}")
        self.cache_exist = os.path.isfile(self.cache_path)
        if self.cache_exist:
            logger.warning(f"using cache: {self.cache_path}")
            self.cache = self._read_cahce()
            self.length = self.cache['length']
            self.index_map = self.cache['index_map']
        else:
            logger.info("no cache detect, will create a cache file, this operation may take a few minutes")
            logger.info(f"cahce file will save at: {self.cache_path}")
        
        if self.length is None:
            self.length,self.index_map = self._count_data()
            self.cache['length'] = self.length
            self.cache['index_map'] = self.index_map

        self._write_cache()

    @staticmethod
    def clean_cache():
        cache_paths = glob.glob(os.path.join(os.getcwd(),'.pjl_cache','.pjl_cache.*'))
        logger.warning(f"detect cahce files: {cache_paths}")
        for cache_path in cache_paths:
            if os.path.isfile(cache_path):
                os.remove(cache_path)
    
    def _count_data(self):
        length = 0
        index_map = {}

        for i,file_path in enumerate(self.files):
            print(f"{file_path}, {length}, {int((i/len(self.files))*100)}%   ",end='\r')

            if  platform == "linux" or platform == "linux2":
                import subprocess
                lines = int(subprocess.check_output(['wc', '-l', file_path]).split()[0])
            else:
                with open(file_path,'r') as f:
                    lines = f.read().strip().split("\n")
                    lines = len(lines)

            length += lines
            index_map[os.path.basename(file_path)] = lines

        return length,index_map
    
    def _read_cahce(self):
        with open(self.cache_path,'r') as f:
            return json.load(f)

    def _write_cache(self):
        with open(self.cache_path,'w') as f:
            json.dump(self.cache,f)
    
    @lru_cache(maxsize=int(os.environ.get('PJL_CACHE_SIZE',100)))
    def _compute_file_and_index(self,i):
        _length = 0
        file_index = None
        for file in self.files:
            _length += self.index_map[os.path.basename(file)]
            if (_length - 1) >= i:
                file_index = (_length-1) - i
                return file,file_index
        raise IndexError
    
    @lru_cache(maxsize=int(os.environ.get('PJL_CACHE_SIZE',100)))
    def _open_file(self,file_path):
        return open(file_path,'r').read().strip().split("\n")
                
    def __getitem__(self,i):
        file, file_index = self._compute_file_and_index(i)
        rows = self._open_file(file_path=file)
        data = rows[file_index]
        data = json.loads(data)
        return data
    
    def __len__(self):
        return self.length
