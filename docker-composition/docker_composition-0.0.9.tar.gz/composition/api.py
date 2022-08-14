import subprocess


def is_compose_installed():
    return compose_cmd("docker-compose", "version").returncode == 0


def compose_cmd(*args):
    return subprocess.run(args, capture_output=True, text=True, shell=True)
