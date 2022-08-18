from . import _jars
import os
import pathlib
import subprocess
import importlib.resources


__version__ = "0.0.1.dev0"

_JAR_NAME = "utilities.jar"

_LOOKUP_PROPERTIES_CLASS_NAME = "LookupProperty"


def _jar():
    return importlib.resources.path(_jars.__package__, _JAR_NAME)


def _java_executable():
    return "java.exe" if os.name == "nt" else "java"


def _java_path_from_home():
    java_home = os.environ.get("JAVA_HOME")
    return pathlib.Path(java_home) / "bin" / _java_executable() if java_home else None


def _process_args(jar, class_name, program_args, *, java_executable=None, use_env=True):
    if not java_executable and use_env:
        java_executable = _java_path_from_home()
    if not java_executable:
        java_executable = _java_executable()
    return [str(java_executable), "-cp", str(jar), class_name] + program_args


def lookup_property(property_name, *, java_executable=None, use_env=True):
    with _jar() as jar:
        process = subprocess.Popen(
            _process_args(
                jar,
                _LOOKUP_PROPERTIES_CLASS_NAME,
                [property_name],
                java_executable=java_executable,
                use_env=use_env,
            ),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        exit_code = process.wait()
        if exit_code == 0:
            return stdout
        elif exit_code == 2 and stderr and stderr.startswith("Not found"):
            return None
        else:
            raise Exception(f"Exit code {exit_code}: {stderr}")


def java_home(*, java_executable=None, use_env=True):
    return lookup_property(
        "java.home", java_executable=java_executable, use_env=use_env
    )
