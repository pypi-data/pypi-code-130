from dynaconf import Dynaconf, Validator
import os
import pathlib

# file current directory used for relative 'configs' folder access.
current_directory = os.path.dirname(os.path.realpath(__file__))

txp_src_directory = pathlib.Path(current_directory).parents[0]

settings = Dynaconf(settings_files=[f"{current_directory}/configs/settings.toml"])
