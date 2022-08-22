""" Python introspection tool """

from .extractor import Extractor
from .abstract import AExporter
from .exporter import JSExporter, JSONExporter, HTMLExporter
from typing import Type

__version__ = "0.0.1"

exporters: dict[str, Type[AExporter]] = {
    "js": JSExporter,
    "json": JSONExporter,
    "html": HTMLExporter,
}

def extract(targets, out: str | None = None):
    e = Extractor()
    e.extract(targets)
    if not out:
        return e.maze

    try: 
        _, ext = out.rsplit(".", 1)
        exporter = exporters[ext](e.maze)
    except:
        exporter = JSONExporter(e.maze)
    
    exporter.export(out)
