from __future__ import absolute_import
import os
import sys
import time

from fs.osfs import OSFS
from zetsubou.commands.base_command import CommandContext, Command
from zetsubou.commands.command_registry import get_all_commands

from zetsubou.logo import print_logo
from zetsubou.project.runtime.project_loader import ProjectError
from zetsubou.utils import logger
from zetsubou.utils.cmd_arguments import parse_arguments
from zetsubou.utils.error_codes import EErrorCode, ReturnErrorcode
from zetsubou._version import get_author_desc

def main() -> int:
    desc = f'FASTbuild project generator for the helpless\n{get_author_desc()}'
    progname = 'zetsubou'
    start_time = time.time()
    logger.Initialize()

    try:
        # populate command list
        command_registry = get_all_commands()

        # parse cmd arguments
        zet_args, zet_commands = parse_arguments(sys.argv[1:], progname, desc, command_registry)

        if len(zet_commands) == 0:
            print ('No command, nothing to do!')
            return 0

        if not zet_args.nologo and not zet_args.silent:
            print_logo(desc)

        if zet_args.silent:
            logger.SetLogLevel(logger.ELogLevel.Silent)
        elif zet_args.verbose:
            logger.SetLogLevel(logger.ELogLevel.Verbose)

        fs_root = os.path.dirname(os.path.normpath(os.path.join(os.getcwd(), zet_args.project)))
        command_context = CommandContext(
            command_args = zet_args,
            fs_root = fs_root,
            project_file = os.path.basename(zet_args.project),
            project_fs = OSFS(fs_root)
        )

        logger.Info(f"Current working directory - '{os.getcwd()}'")
        logger.Info(f"Project working directory - '{fs_root}'")

        for command_name in zet_commands:
            command : Command = command_registry[command_name]
            command.Execute(command_context)

        end_time = time.time()

        if not zet_args.silent:
            print(f'\nFinished in {end_time - start_time:.2f} sec')

        return 0

    except ReturnErrorcode as errcode:
        logger.ReturnCode(errcode.error_code)
        return errcode.error_code.value

    except ProjectError as proj_error:
        logger.Error(proj_error)
        logger.ReturnCode(EErrorCode.UNKNOWN_ERROR)
        return 666

    except Exception as error:
        logger.Exception(error)
        return 666

# Process draft:
# OS required:
# - python 3.x
# - conan
# - vstudio
# Install process:
# - venc setup
#   - conan installs dev dependencies:
#     - zetsubou
#     - fastbuild
# - call vswhere
# - process yml
# - generate files
# zet install
# installing dev virtual environment...
# zet create - emit template for something
# zet install - install virtual environment
# zet config - emit fastbuild files
# zet build - call build on fastbuild
# zet clean - clean generated files
# zet list - list all commands
# zet clean install config build