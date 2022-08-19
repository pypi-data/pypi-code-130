from __future__ import annotations

import argparse

from dismod.dependency import DependencyContainer
from dismod.dot import render
from dismod.instruction import (
    get_import_instructions,
    get_instructions_from_file,
    parse_instructions,
)
from dismod.utils import collect_files_in_module


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dismod",
        description="Generate dependency graphs for your codebase.",
    )

    parser.add_argument(
        "filepath",
        metavar="filepath",
        type=str,
        help="The path to the source code in your project.",
    )
    parser.add_argument(
        "--split-files",
        action="store_true",
        default=False,
        help="Render the output as split files",
    )
    parser.add_argument("--ignore-folder", help="Ignore a specific folder")
    parser.add_argument(
        "--rankdir",
        default="LR",
        help="Sets the direction of the graph. See also: https://graphviz.org/docs/attrs/ratio/",  # noqa: E501
    )
    parser.add_argument(
        "--overlap",
        default="scale",
        help="Determine if and how node overlaps should be removed. See also: https://graphviz.org/docs/attrs/overlap/",  # noqa: E501
    )
    parser.add_argument(
        "--ratio",
        default="fill",
        help="Sets the aspect ratio (drawing height/drawing width) for the drawing. See also: https://graphviz.org/docs/attrs/ratio/",  # noqa: E501
    )
    parser.add_argument(
        "--fontsize",
        default="16",
        help="The size of the font to be used. See also: https://graphviz.org/docs/attrs/fontsize/",  # noqa: E501
    )
    parser.add_argument(
        "--dpi",
        default="150",
        help="Specifies the expected number of pixels per inch on a display device. See also: https://graphviz.org/docs/attrs/dpi/",  # noqa: E501
    )
    parser.add_argument(
        "--shape",
        default="rectangle",
        help="Sets the shape of a node. See also: https://graphviz.org/docs/attrs/shape/",  # noqa: E501
    )
    parser.add_argument(
        "--fontname",
        default="Consolas",
        help="Font used for text. See also: https://graphviz.org/docs/attrs/fontname/",  # noqa: E501
    )
    return parser


def get_import_dependency_list(files: list[str]) -> list[DependencyContainer]:
    import_dependency_list = []

    for file in files:
        instructions = get_instructions_from_file(filepath=file)
        all_instructions = get_import_instructions(instructions=instructions)
        # Early exit, we don't care about files that don't have any import
        # statements, e.g; __init__.py or other simple file that has no import
        if not all_instructions:
            continue

        instructions_normalized = parse_instructions(
            instructions=all_instructions,
        )

        file_import_dependencies = DependencyContainer(filepath=file)
        file_import_dependencies.add_import(instructions_normalized)
        import_dependency_list.append(file_import_dependencies)
    return import_dependency_list


def main() -> int:
    parser = create_argument_parser()
    args = parser.parse_args()

    # Collect all files that lives in the specified filepath
    files = collect_files_in_module(
        filepath=args.filepath,
        ignore_folder=args.ignore_folder,
    )
    # Get a list of import dependencies for each file
    list_of_dependencies = get_import_dependency_list(files=files)

    render(
        project_name=args.filepath,
        dependency_containers=list_of_dependencies,
        rankdir=args.rankdir,
        overlap=args.overlap,
        ratio=args.ratio,
        fontsize=args.fontsize,
        dpi=args.dpi,
        shape=args.shape,
        fontname=args.fontname,
        split_files=args.split_files,
    )

    return 0
