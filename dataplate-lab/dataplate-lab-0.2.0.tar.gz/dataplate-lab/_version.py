import json
from pathlib import Path

__all__ = ["__version__"]

def _fetchVersion():
    return "0.2.0"
    # HERE = Path(__file__).parent.resolve()
    #
    # for settings in HERE.rglob("package.json"):
    #     try:
    #         with settings.open() as f:
    #             version = json.load(f)["version"]
    #             return (
    #                 version.replace("-alpha.", "a")
    #                 .replace("-beta.", "b")
    #                 .replace("-rc.", "rc")
    #             )
    #     except FileNotFoundError:
    #         pass
    #
    # raise FileNotFoundError(f"Could not find package.json under dir {HERE!s}")

__version__ = _fetchVersion()


# from collections import namedtuple
#
# VersionInfo = namedtuple(
#     "VersionInfo", ["major", "minor", "micro", "releaselevel", "serial"]
# )
#
# # DO NOT EDIT THIS DIRECTLY!  It is managed by bumpversion
# version_info = VersionInfo(0, 1, 0, "final", 0)
#
# _specifier_ = {"alpha": "a", "beta": "b", "candidate": "rc", "final": ""}
#
# __version__ = "{}.{}.{}{}".format(
#     version_info.major,
#     version_info.minor,
#     version_info.micro,
#     (
#         ""
#         if version_info.releaselevel == "final"
#         else _specifier_[version_info.releaselevel] + str(version_info.serial)
#     ),
# )