import copy
import os
import pathlib
import tempfile

from helper.artifact import ArtifactTypes
from helper.docker import Docker
from helper.logging import CriticalException
from rule.rules.abstract import AbstractExecutionRule, AbstractFileResult
from rule.rules.file import assert_unique_file_paths


class ImageResult(AbstractFileResult):
    def __init__(self, data):
        self.data = data

    def get_file(self):
        return self

    def get_files(self):
        return [self]


class ImageRule(AbstractExecutionRule):
    @classmethod
    def _args_to_kwargs(cls, args):
        return {'image_name': args[0]}

    def _get_inputs(self):
        return {'image_name'}

    def _str(self):
        return self.image_name

    @classmethod
    def run(cls, inputs):
        if '@sha256:' not in inputs['image_name']:
            raise CriticalException(f'Failed to pull {inputs["image_name"]}. External image requires sha256 code in name.')

        return ImageResult(Docker().pull_image(inputs['image_name'])), None

    @staticmethod
    def get_yaml_tag():
        return u'!image'


class ImageBuildRule(AbstractExecutionRule):
    IMPORT_FILE_INSTRUCTIONS = {'ADD', 'COPY'}
    run_with_result_inputs = False

    def _get_inputs(self):
        return {'dockerfile', 'args', 'files'}

    def _str(self):
        return self.dockerfile.path

    @classmethod
    def run(cls, inputs):
        assert_unique_file_paths(inputs['files'])

        docker_client = Docker()
        build_args = copy.deepcopy(inputs['args'])

        for build_arg_k, build_arg_v in list(build_args.items()):
            if isinstance(build_arg_v, ImageResult):
                build_args[build_arg_k] = docker_client.load_images(build_args[build_arg_k].get_file().data)[0]

        with tempfile.TemporaryDirectory() as tmp_dir:
            for file_path in inputs['files']:
                for file in file_path.get_files():
                    path_relative_to_dockerfile = file.path.relative_to(inputs['dockerfile'].path.parent)
                    file_path = pathlib.Path(tmp_dir).joinpath(path_relative_to_dockerfile)
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(str(file_path), 'wb') as f:
                        f.write(file.data)

            with open(os.path.join(tmp_dir, 'Dockerfile'), 'wb') as f:
                f.write(inputs['dockerfile'].get_file().data)

            return ImageResult(docker_client.build_from_bytes(tmp_dir, build_args=build_args)), None

    def __init__(self, *args, **kwargs):
        if 'args' not in kwargs:
            kwargs['args'] = {}
        if 'files' not in kwargs:
            kwargs['files'] = []

        super().__init__(*args, **kwargs)

    @staticmethod
    def get_yaml_tag():
        return u'!image_build'


class ImageTagRule(AbstractExecutionRule):
    def _get_inputs(self):
        return {'image', 'image_name', 'tags'}

    def _str(self):
        return self.image_name

    @classmethod
    def run(cls, inputs):
        docker_client = Docker()
        tagged_images = docker_client.load_images(inputs['image'].get_file().data, inputs['image_name'], inputs['tags'])
        artifacts = [(ArtifactTypes.IMAGE_TAG, tag) for tag in tagged_images]

        return tagged_images, artifacts

    def __init__(self, *args, **kwargs):
        if 'tags' not in kwargs:
            kwargs['tags'] = ['latest']

        super().__init__(*args, **kwargs)

    @staticmethod
    def get_yaml_tag():
        return u'!image_tag'
