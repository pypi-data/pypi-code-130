"""Filesystem handling"""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path


def read(root, path):
    env = Environment(
        loader=FileSystemLoader((root)),
        autoescape=select_autoescape())
    template = env.get_template(str(path))
    return template.render()


def build(root):
    build_dir = Path("build")

    for path, _, files in os.walk(root):
        rel_dir = Path(path).relative_to(root)  # Strip containing dir
        output_dir = build_dir/rel_dir          # Prepend build dir

        # Make output dir, if doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        for name in files:
            # Underscore flags to not render---useful for partials
            if name[0] == "_":
                continue
            
            with (output_dir/name).open("w+") as f:
                f.write(read(root, rel_dir/name))
