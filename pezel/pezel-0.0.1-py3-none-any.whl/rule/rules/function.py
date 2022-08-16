import io
import os
import pathlib
import pystache
import tarfile
import uuid

from helper.dictionary import flatten_dict, set_nested_dict
from helper.docker import Docker
from helper.logging import CriticalException, user_log_root
from rule.rules.abstract import AbstractExecutionRule
from rule.rules.file import FileResult, PathResult, assert_unique_file_paths


user_log = user_log_root.getChild(__name__)


class FunctionRule(AbstractExecutionRule):
    @staticmethod
    def _format_command(command):
        if isinstance(command, list):
            commands = command
        else:
            commands = [command]

        new_commands = []
        for command in commands:
            if isinstance(command, str):
                new_command = {'cmd': command}
            else:
                new_command = command
            new_commands.append(new_command)

        return new_commands

    def _get_inputs(self):
        return {'current_dir', 'root_path', 'host_root_path', 'command', 'default_args', 'image', 'volumes', 'environment'}

    def _str(self):
        return self.command

    def __init__(self, *args, **kwargs):
        if 'command' in kwargs:
            kwargs['command'] = self._format_command(kwargs['command'])
        if 'default_args' not in kwargs:
            kwargs['default_args'] = {}
        if 'volumes' not in kwargs:
            kwargs['volumes'] = None
        if 'environment' not in kwargs:
            kwargs['environment'] = None

        super().__init__(*args, **kwargs)

    @classmethod
    def run(cls, inputs):
        # Force host path to use absolute path
        if inputs['volumes'] is not None:
            if inputs['host_root_path'] is None:
                raise CriticalException('Missing argument host root path argument while using volumes function.')

            user_log.warn('Using volumes can cause unreliable builds.')

            host_current_dir = inputs['host_root_path'].joinpath(inputs['current_dir'].relative_to(inputs['root_path']))
            if isinstance(inputs['volumes'], dict):
                inputs['volumes'] = {
                    str(host_current_dir.joinpath(volume).resolve()): volume_data
                    for volume, volume_data in inputs['volumes'].items()}
            else:
                inputs['volumes'] = [
                    str(host_current_dir.joinpath(volume).resolve())
                    for volume in inputs['volumes']]

        return {
            'default_args': inputs['default_args'],
            'image': inputs['image'],
            'command': inputs['command'],
            'environment': inputs['environment'],
            'volumes': inputs['volumes']}, None

    @staticmethod
    def get_yaml_tag():
        return u'!function'


class RunRule(AbstractExecutionRule):
    @staticmethod
    def _add_folder_to_tar(path, tar):
        info = tarfile.TarInfo(str(path))
        info.type = tarfile.DIRTYPE
        tar.addfile(info)

    def _get_inputs(self):
        return {'current_dir', 'root_path', 'function', 'include', 'args', 'out', 'workdir'}

    def _str(self):
        return self.function.node_id

    @classmethod
    def run(cls, inputs):
        container_tmp_dir = pathlib.Path('/tmp').joinpath(str(uuid.uuid4()))
        container_tmp_data_dir = container_tmp_dir.joinpath('data')
        container_tmp_out_dir = container_tmp_dir.joinpath('out')
        commands_args = {**inputs['function']['default_args'], **inputs['args'], 'out': {}}
        container_kwargs = {
            'environment': inputs['function']['environment'],
            'volumes': inputs['function']['volumes'],
            'working_dir': str(container_tmp_data_dir.joinpath(inputs['workdir'].path.relative_to(inputs['root_path'])))
            if inputs['workdir'] is not None else None}

        file_commands_args = []
        for commands_args_k, commands_args_v in flatten_dict(commands_args):
            if isinstance(commands_args_v, PathResult):
                file_commands_args.append((commands_args_k, commands_args_v))

        file_environments = []
        if container_kwargs['environment'] is not None:
            for environment_name, environment_value in list(container_kwargs['environment'].items()):
                if isinstance(environment_value, PathResult):
                    file_environments.append((environment_name, environment_value))

        assert_unique_file_paths([v for k, v in file_commands_args] + [v for k, v in file_environments] + inputs['include'])

        file_archive = io.BytesIO()
        with tarfile.open(fileobj=file_archive, mode='w:gz') as tar:
            for out_name in inputs['out']:
                out_file = pathlib.Path(out_name)
                container_file_path = container_tmp_out_dir.joinpath(out_file)
                commands_args['out'][out_name] = str(container_file_path)
                cls._add_folder_to_tar(container_file_path.parent, tar)

            for commands_args_k, commands_args_v in file_commands_args:
                command_path = commands_args_v.add_to_tar(tar, container_tmp_data_dir, inputs['root_path'])
                set_nested_dict(commands_args, commands_args_k, str(command_path))

            for include_path in inputs['include']:
                include_path.add_to_tar(tar, container_tmp_data_dir, inputs['root_path'])

            for environment_name, environment_value in file_environments:
                new_environment_value = environment_value.add_to_tar(tar, container_tmp_data_dir, inputs['root_path'])
                container_kwargs['environment'][environment_name] = str(new_environment_value)

        docker_client = Docker()
        image = docker_client.load_images(inputs['function']['image'].get_file().data)[0]
        commands = [
            {
                **command,
                'cmd': pystache.render(command['cmd'], commands_args),
                'workdir':
                    pystache.render(command['workdir'], commands_args)
                    if command.get('workdir', None) is not None else None}
            for command in inputs['function']['command']]
        result = docker_client.run_command(
            image,
            commands,
            in_files=[('/', file_archive.getvalue())],
            out_files=[v for k, v in flatten_dict(commands_args['out'])],
            container_kwargs=container_kwargs)

        out = {}
        for alias_name, container_path in commands_args['out'].items():
            main_path = inputs['current_dir'].joinpath(alias_name)
            files = []
            for file_path, data in result[container_path].items():
                file_built_from = FileResult.rule_to_str(cls, str([command['cmd'] for command in inputs['function']['command']]))
                files.append(FileResult(main_path.joinpath(file_path), data, built_from=file_built_from))
            out[alias_name] = PathResult(main_path, files)

        return out, None

    def __init__(self, *args, **kwargs):
        if 'include' not in kwargs:
            kwargs['include'] = []
        if 'args' not in kwargs:
            kwargs['args'] = {}
        if 'out' not in kwargs:
            kwargs['out'] = []
        if 'workdir' not in kwargs:
            kwargs['workdir'] = None

        super().__init__(*args, **kwargs)

    @staticmethod
    def get_yaml_tag():
        return u'!run'
