from .library import DockerRun, DockerRunCreateConfig
import argparse

parser = argparse.ArgumentParser(description="Process Docker images.")
subparser = parser.add_subparsers(dest="command")
subparser.required = True
buildparser = subparser.add_parser("build")
parser.add_argument(
    "--level",
    "-l",
    default="INFO",
    help="log level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
)
createconfigparser = subparser.add_parser("createconfig")
createconfigparser.add_argument(
    "--filename", "-n", help="config file names", default="docker.ini", type=str
)

buildparser.add_argument(
    "version",
    default="micro",
    const="micro",
    nargs="?",
    choices=["micro", "minor", "major"],
    help="image patch build version",
)
buildparser.add_argument("push", type=str, nargs="?", help="to push docker images")
buildparser.add_argument(
    "-f", "--filename", help="Config custom file name", default="docker.ini"
)
buildparser.add_argument(
    "-df", "--dockerfile", type=str, help="custom name dockerfile", default="Dockerfile"
)
GETCLASS = dict(
    build=DockerRun,
    createconfig=DockerRunCreateConfig,
)


def main() -> None:
    args = parser.parse_args()
    cls = GETCLASS[args.command](args)
    cls()
