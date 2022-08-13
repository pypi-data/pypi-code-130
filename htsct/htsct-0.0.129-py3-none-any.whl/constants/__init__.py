from os.path import expanduser
from pathlib import Path
from pathlib import PurePath
from typing import IO
from typing import Union
from htsct import statics
import yaml

NameOrFile = Union[str, PurePath, IO]
HTS_HOME = Path(expanduser('~')) / "htsct"
STATIC_PATH = Path(statics.__path__[0])
CALC_FILES = HTS_HOME / "calcs"
DB_URL = ""
SQLALCHEMY_DATABASE_URL = ""
ACTIVE_CONFIG = ""
TASK_DESCRIPTION = ""
if (HTS_HOME / "config.yaml").exists():
    with open(HTS_HOME / "config.yaml") as fd:
        datas = yaml.load(fd, Loader=yaml.FullLoader)
        globals().update({k.upper(): v for k, v in datas.items()})
