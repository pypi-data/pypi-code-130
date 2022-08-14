from PIL import Image
from Pxucz.utils import global_path


def load(path: str):
    return Image.open(global_path.get_path(path=path)).convert("RGBA")
