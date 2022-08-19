import json
import os
from typing import List


class File:
    def __init__(self, filename: str, path: str = './', size: int = 0, isfile: bool = True, *args, **kwargs):
        self.path: str = path
        self.filename: str = filename
        self.size: int = size
        self.isfile: bool = isfile
        self.ext = {}
        self.ext.update(kwargs)
        self.children: List[File] = []

    @property
    def isdir(self):
        return not self.isfile

    def to_json(self):
        res = {}
        res.update(self.ext)
        res.update({
            "path": self.path,
            "size": self.size,
            "isfile": self.isfile,
            "filename": self.filename,
            "children": [file.to_json() for file in self.children]
        })
        return res

    def __str__(self):
        return json.dumps(self.to_json())

    def __repr__(self):
        return self.__str__()


class FileSystem:
    def __init__(self, *args, **kwargs):
        pass

    def isfile(self, path: str) -> bool:
        pass

    def isdir(self, path: str) -> bool:
        pass

    def exists(self, path: str) -> bool:
        pass

    def listdir(self, path: str = None) -> List[File]:
        pass

    def upload(self, src: str, dst: str) -> bool:
        pass

    def download(self, src: str, dst: str) -> bool:
        pass

    def upload_file(self, src_file: str, dst_file: str) -> bool:
        return self.upload(src_file, dst_file)

    def download_file(self, src_file: str, dst_file: str) -> bool:
        return self.download(src_file, dst_file)

    def upload_dir(self, src_dir: str, dst_dir: str) -> bool:
        return self.upload(src_dir, dst_dir)

    def download_dir(self, src_dir: str, dst_dir: str) -> bool:
        return self.download(src_dir, dst_dir)


class OsSystem(FileSystem):
    def __init__(self, *args, **kwargs):
        super(OsSystem, self).__init__(*args, **kwargs)

    def isfile(self, path) -> bool:
        return os.path.isfile(path)

    def isdir(self, path: str) -> bool:
        return os.path.isdir(path)

    def exists(self, path) -> bool:
        return os.path.exists(path)

    def listdir(self, path: str = "./") -> List[File]:
        result = []
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            result.append(File(filename=filename, path=path, isfile=self.isfile(filepath)))
        return result
