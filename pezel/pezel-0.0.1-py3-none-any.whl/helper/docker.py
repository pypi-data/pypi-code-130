import docker
import io
import metadata
import pathlib
import tarfile
import uuid

from docker.errors import APIError, BuildError

from helper.debug import debug_info
from helper.logging import CriticalException, dev_log_root


dev_log = dev_log_root.getChild(__name__)


class Docker(object):
    REPOSITORY = f'{metadata.NAME}_{metadata.VERSION}'

    def __init__(self):
        self.docker_client = docker.from_env()

    def build_from_bytes(self, dir_path, build_args=None):
        if build_args is None:
            build_args = {}

        try:
            image, _ = self.docker_client.images.build(path=dir_path, buildargs=build_args)
        except APIError as err:
            raise CriticalException(str(err))
        except BuildError as err:
            build_log = {'stream': [], 'error': []}
            for log in err.build_log:
                if 'stream' in log:
                    build_log['stream'].append(log['stream'])
                elif 'error' in log:
                    build_log['error'].append(log['error'])
                else:
                    dev_log.warn(f'Unknown BuildError log: {log}')

            raise CriticalException('\n'.join(build_log['stream']) + str(err))

        image_bytes = bytearray()
        for chunk in image.save(chunk_size=None):
            image_bytes.extend(chunk)

        return image_bytes

    def load_images(self, images, name=None, tags=None):
        loaded_images = self.docker_client.images.load(images)

        if name is None:
            name = self.REPOSITORY

        if tags is None:
            build_uuid = str(uuid.uuid4())
            tags = [f'{build_uuid}_{image_i}' for image_i in range(len(loaded_images))]

        image_tags = []
        for image, tag in zip(loaded_images, tags):
            image.tag(name, tag)
            image_tags.append(f'{name}:{tag}')

        return image_tags

    def pull_image(self, name):
        image = self.docker_client.images.pull(name)

        image_bytes = bytearray()
        for chunk in image.save(chunk_size=None):
            image_bytes.extend(chunk)

        return image_bytes

    def run_command(self, image, commands, in_files=None, out_files=None, container_kwargs=None):
        if in_files is None:
            in_files = []
        if out_files is None:
            out_files = []
        if container_kwargs is None:
            container_kwargs = {}

        container = self.docker_client.containers.create(image, 'sh', tty=True, **container_kwargs)
        container.start()
        for path, data in in_files:
            container.put_archive(path, data)

        command_outputs = []
        for command in commands:
            sanitized_cmd = command["cmd"].replace('"', '\\"')
            exit_code, output = container.exec_run(
                cmd=f'bash -c "{sanitized_cmd}"',
                workdir=command.get('workdir', None))
            command_outputs.append(output.decode())
            if exit_code != 0:
                running_container_name = None
                if not debug_info.keep_failed_container_alive:
                    container.kill()
                else:
                    running_container_name = container.name

                err_log = []
                for err_log_command, err_log_command_output in zip(commands, command_outputs):
                    err_log.append(f'${err_log_command["cmd"]}')
                    err_log.append(err_log_command_output)
                err_log.append(f'Got exit code {exit_code} when running "{command["cmd"]}".')

                error = CriticalException('\n'.join(err_log))
                error.set_failed_execution_docker(image, running_container_name)
                raise error

        out = {}
        for out_file in out_files:
            tarfile_data_stream, _ = container.get_archive(out_file)
            tarfile_bytes = bytearray()
            for chunk in tarfile_data_stream:
                tarfile_bytes.extend(chunk)
            with tarfile.open(fileobj=io.BytesIO(tarfile_bytes)) as tar:
                files = {}
                for member in tar.getmembers():
                    if not member.isfile():
                        continue
                    name = pathlib.Path(member.name).relative_to(pathlib.Path(out_file).name)
                    files[name] = tar.extractfile(member).read()

                out[out_file] = files

        container.kill()

        return out
