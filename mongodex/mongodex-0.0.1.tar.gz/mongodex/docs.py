from typing import Iterable

from .helpers import Index

HEADER = """
| Index name | Fields | Comment | Properties
| --- | --- | --- | --- |
"""


def md_generator(
    collections: Iterable[Index], output_file: str = "MONGODEX_INDEXES.md"
):
    with open(output_file, "w") as f:
        for collection, indexes in collections.items():
            f.write(f"\n## Collection: **{collection}**\n")
            f.write(HEADER)
            for index in indexes:
                f.write(f"| {index.name} |")
                f.write(f" {index.fields} |")
                f.write(f" {index.comment} |")
                f.write(f" {index.properties} |")
                f.write("\n")
