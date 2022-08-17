import os
import shutil
from typing import Any, Callable, Dict, List, Optional

def nst_datamover(archive_path: str, language: str) -> None:
    id_path = archive_path.rsplit("_", maxsplit=1)[0]
    if "lydfiler" not in id_path:
        return
    src = os.path.join(archive_path, language)
    dst = os.path.join(id_path, language)

    for sub_file in os.listdir(src):
        os.makedirs(dst, exist_ok=True)
        shutil.move(os.path.join(src, sub_file), os.path.join(dst, sub_file))

    shutil.rmtree(archive_path)

def storting_datamover(archive_path: str, *_: List[Any]) -> None:
    head_folder = os.path.split(archive_path)[0]
    for _folder in os.listdir(archive_path):
        src = os.path.join(archive_path, _folder)
        dst = os.path.join(head_folder, _folder)
        shutil.move(src=src, dst=dst)

    shutil.rmtree(archive_path)

def get_datamover(name: str) -> Optional[Callable[..., None]]:
    datamovers: Dict[str, Callable[..., None]] = {
        "storting": storting_datamover,
        "nst": nst_datamover,
    }

    if datamovers.get(name):
        return datamovers.get(name)
    return None
