"""Contains a cmd entry point to create a plugin docker image with plugin info labels."""
import os
from shlex import join
import subprocess  # nosec
import sys

from logbook import INFO, Logger  # type: ignore

from hansken_extraction_plugin.framework import GRPC_API_VERSION
from hansken_extraction_plugin.runtime.reflection_util import get_plugin_class

log = Logger(__name__)
log.level = INFO

usage_explanation = ('Usage: {} [-h] [--help] PLUGIN_FILE DOCKER_FILE_DIRECTORY [DOCKER_IMAGE_NAME] [DOCKER_ARGS]\n'
                     '  PLUGIN_FILE: Path to the python file of the plugin.\n'
                     '  DOCKER_FILE_DIRECTORY: Path to the directory containing the Dockerfile of the plugin.\n'
                     '  (Optional) [DOCKER_IMAGE_NAME]: Name of the docker image without tag. Note that docker '
                     'image names cannot start with a period or dash.\n '
                     '                                 If it starts with a dash, it will be '
                     'interpreted as an additional docker argument (see next).\n'
                     '  (Optional) [DOCKER_ARGS]: Additional arguments for the docker command, which can be as '
                     'many arguments as you like.\n'
                     'Example: build_plugin plugin.py . imagename --build-arg https_proxy="$https_proxy"')


def _build(plugin_class, docker_file, name=None, docker_args=None):
    """
    Build an Extraction Plugin docker image according to provided arguments.

    :param plugin_class:  The class implementing BaseExtractionPlugin
    :param docker_file: Path to the directory containing the Dockerfile of the plugin.
    :param name: Name of the docker image without tag. Note that docker
            image names cannot start with a period or dash. If it starts with a dash, it will be
            interpreted as an additional docker argument (see next).
    :param docker_args: Additional arguments for the docker command, which can be as
            many arguments as you like.
    :return: returncode of the docker command
    """
    plugin_info = plugin_class().plugin_info()

    plugin_id = str(plugin_info.id)
    labels = {
        'org.hansken.plugin-info.id': plugin_id,
        'org.hansken.plugin-info.id-domain': plugin_info.id.domain,
        'org.hansken.plugin-info.id-category': plugin_info.id.category,
        'org.hansken.plugin-info.id-name': plugin_info.id.name,
        'org.hansken.plugin-info.version': plugin_info.version,
        'org.hansken.plugin-info.api-version': GRPC_API_VERSION,
        'org.hansken.plugin-info.description': plugin_info.description,
        'org.hansken.plugin-info.webpage': plugin_info.webpage_url,
        'org.hansken.plugin-info.deferred-iterations': plugin_info.deferred_iterations,
        'org.hansken.plugin-info.matcher': plugin_info.matcher,
        'org.hansken.plugin-info.license': plugin_info.license,
        'org.hansken.plugin-info.maturity-level': plugin_info.maturity.name,
        'org.hansken.plugin-info.author-name': plugin_info.author.name,
        'org.hansken.plugin-info.author-organisation': plugin_info.author.organisation,
        'org.hansken.plugin-info.author-email': plugin_info.author.email,
    }

    if plugin_info.resources:
        labels['org.hansken.plugin-info.resource-max-cpu'] = plugin_info.resources.maximum_cpu
        labels['org.hansken.plugin-info.resource-max-mem'] = plugin_info.resources.maximum_memory

    if not name:
        name = f'extraction-plugins/{plugin_id}'

    command = ['docker', 'build',
               docker_file,
               '-t', f'{name}:{plugin_info.version}'.lower(),
               '-t', f'{name}:latest'.lower()]

    for (label, value) in labels.items():
        command.append('--label')
        command.append(f'{label}={value}')

    command.extend(docker_args)

    log.info(f' -> Invoking Docker build with command: {join(command)}')
    os.environ['SYSTEMD_COLORS'] = '1'

    # execute the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  # nosec

    # print the output of the command
    for c in iter(lambda: process.stdout.read(1), b''):
        sys.stdout.buffer.write(c)
        sys.stdout.flush()
    process.wait()

    if process.returncode != 0:
        raise RuntimeError(f' -> DOCKER BUILD FAILED (see logs above this line for more details)\n'
                           f'    command was: {join(command)}')
    else:
        log.info(' -> Docker build finished')
    return process.returncode


def _build_using_plugin_file(plugin_file, docker_file, name=None, docker_args=None):
    plugin_class = get_plugin_class(plugin_file)

    if plugin_class is not None:
        _build(plugin_class, docker_file, name, docker_args)
    else:
        raise ValueError(f'No Extraction Plugin class found in {plugin_file}')


def _parse_args(argv):
    argcount = len(argv)
    if argcount > 0 and (argv[0] == '-h' or argv[0] == '--help'):
        log.info(usage_explanation)
        print(usage_explanation)
        return None

    if argcount < 2:
        raise ValueError('Wrong number of arguments! \n' + usage_explanation)

    plugin_file = argv[0]
    docker_file = argv[1]
    # oci image names cannot start with a dash, so if this arg starts with a dash
    # omit the name arg and expect it to be an extra docker arg
    omit_name = len(argv) <= 2 or argv[2].startswith('-')
    name = None if omit_name else argv[2]
    docker_args_start_pos = 2 if omit_name else 3
    docker_args = [] if len(argv) <= docker_args_start_pos else argv[docker_args_start_pos:]
    return plugin_file, docker_file, name, docker_args


def main():
    """Build an Extraction Plugin docker image according to provided arguments."""
    parsed = _parse_args(sys.argv[1:])
    if parsed:
        plugin_file, docker_file, name, docker_args = parsed
        _build_using_plugin_file(plugin_file, docker_file, name, docker_args)
