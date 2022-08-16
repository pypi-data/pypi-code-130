import hashlib
import io
import pathlib
import tarfile
import urllib.request
import yaml

from helper.logging import CriticalException
from rule.rules.abstract import AbstractExecutionRule, AbstractRule, AbstractFileResult


class FileResult(object):
    def __init__(self, path, data=None, mode=0o744, built_from=None):
        self.path = path
        self.data = data
        self.mode = mode
        self.built_from = built_from

    def add_to_tar(self, tar, path):
        info = tarfile.TarInfo(str(path))
        info.size = len(self.data)
        info.mode = self.mode
        tar.addfile(info, io.BytesIO(initial_bytes=self.data))

    def exists(self):
        return self.data is not None

    @staticmethod
    def rule_to_str(rule, unique_data):
        return f'{rule.get_yaml_tag()} ({unique_data})'

    def str(self):
        if self.built_from is None:
            return f'Local file {self.path}'

        return f'Built file from {self.built_from}'


class PathResult(AbstractFileResult):
    def __init__(self, path, files):
        self.path = path
        self.files = files

    def add_to_tar(self, tar, path, root_path):
        for file in self.files:
            if file.exists():
                file_path = path.joinpath(file.path.relative_to(root_path))
                file.add_to_tar(tar, file_path)

        return path.joinpath(self.path.relative_to(root_path))

    def get_file(self):
        if len(self.files) == 0:
            raise CriticalException('Expecting a single file, found no file.')
        elif len(self.files) > 1:
            raise CriticalException('Expecting a single file, found more than one.')

        return self.files[0]

    def get_files(self):
        return self.files


class DownloadRule(AbstractExecutionRule):
    def _get_inputs(self):
        return {'current_dir', 'url', 'path', 'sha256'}

    def _str(self):
        return self.url

    @classmethod
    def run(cls, inputs):
        with urllib.request.urlopen(inputs['url']) as f:
            data = f.read()

        data_hash = hashlib.sha256(data).hexdigest()
        if data_hash != inputs['sha256']:
            raise CriticalException(f'Hash {data_hash} doesn\'t match {inputs["sha256"]} for file {inputs["path"]}.')

        file_built_from = FileResult.rule_to_str(cls, inputs["url"])
        file = FileResult(inputs['current_dir'].joinpath(inputs['path']), data, built_from=file_built_from)
        return PathResult(file.path, [file]), None

    @staticmethod
    def get_yaml_tag():
        return u'!download'


class FileRule(AbstractExecutionRule):
    @classmethod
    def _args_to_kwargs(cls, args):
        return {'path': args[0]}

    def _get_inputs(self):
        return {'current_dir', 'path'}

    def _str(self):
        return self.path

    @classmethod
    def run(cls, inputs):
        full_path = inputs['current_dir'].joinpath(inputs['path'])
        with open(full_path, "rb") as f:
            file_bytes = f.read()

        file = FileResult(full_path, file_bytes)
        return PathResult(file.path, [file]), None

    @staticmethod
    def get_yaml_tag():
        return u'!file'


class FolderRule(AbstractExecutionRule):
    @classmethod
    def _args_to_kwargs(cls, args):
        return {'path': args[0]}

    def _get_inputs(self):
        return {'current_dir', 'path'}

    def _str(self):
        return self.path

    @classmethod
    def run(cls, inputs):
        full_path = inputs['current_dir'].joinpath(inputs['path'])
        files = []
        for path in full_path.rglob('*'):
            if not path.is_file():
                continue

            with open(path, "rb") as f:
                file_bytes = f.read()
            files.append(FileResult(path, file_bytes))

        return PathResult(full_path, files), None

    @staticmethod
    def get_yaml_tag():
        return u'!folder'


class GlobRule(AbstractRule):
    @classmethod
    def from_yaml(cls, root_path, loader, yaml_node, host_root_path=None):
        data = {'patterns': [], 'ignore_folders': False}
        if isinstance(yaml_node.node, yaml.ScalarNode):
            data['patterns'] = [yaml_node.get_value(loader)]
        elif isinstance(yaml_node.node, yaml.SequenceNode):
            data['patterns'] = yaml_node.get_value(loader)
        elif isinstance(yaml_node.node, yaml.MappingNode):
            data = yaml_node.get_value(loader)
        else:
            raise CriticalException(f'Unknown glob Node type {type(yaml.MappingNode)}.')

        paths = []
        current_dir = yaml_node.current_dir
        for pattern in data['patterns']:
            current_path_pattern = current_dir.relative_to(root_path).joinpath(pathlib.Path(pattern))
            root_path_pattern = root_path.joinpath(current_path_pattern.relative_to(current_path_pattern.anchor))
            paths.extend(current_dir.rglob(str(root_path_pattern.relative_to(current_dir))))

        if data['ignore_folders']:
            paths = [path for path in paths if not path.is_dir()]

        return [FileRule(root_path, yaml_node, file_path) for file_path in paths]

    @staticmethod
    def get_yaml_tag():
        return u'!glob'


class PathRule(AbstractExecutionRule):
    @classmethod
    def _args_to_kwargs(cls, args):
        return {'path': args[0]}

    def _get_inputs(self):
        return {'current_dir', 'path'}

    def _str(self):
        return self.path

    @classmethod
    def run(cls, inputs):
        full_path = inputs['current_dir'].joinpath(inputs['path'])
        return PathResult(full_path, [FileResult(full_path)]), None

    @staticmethod
    def get_yaml_tag():
        return u'!path'


def assert_unique_file_paths(path_results):
    found_paths = {}
    dupe_paths = {}
    for path_result in path_results:
        for file in path_result.get_files():
            if file.path not in found_paths:
                found_paths[file.path] = [file]
            else:
                found_paths[file.path].append(file)
                dupe_paths[file.path] = found_paths[file.path]

    if dupe_paths:
        dupe_file_strs = []
        for dupe_file_path, dupe_files in dupe_paths.items():
            dupe_file_strs.append(
                f'{", ".join([dupe_file.str() for dupe_file in dupe_files])} have the same path {dupe_file_path}')

        conflicts = '\n'.join(dupe_file_strs)
        raise CriticalException(f'Found {len(dupe_paths)} duplicate file path conflict(s):\n{conflicts}')
