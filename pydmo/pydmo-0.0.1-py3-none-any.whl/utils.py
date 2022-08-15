import os
from pathlib import Path

ROOT_DIR: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".."

DIR2TEST_DATABASE = ROOT_DIR / "tests" / "data"
