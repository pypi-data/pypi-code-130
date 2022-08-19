from __future__ import annotations

import os

from dismod.dependency import DependencyContainer

DOT_TEMPLATE = """\
digraph "%s" {
    graph [
        rankdir="%s",
        overlap="%s",
        ratio="%s",
        fontsize="%s",
        dpi="%s",
    ];
    node [
        fontsize="%s"
        shape="%s"
        fontname="%s"
    ];

    %s}
"""


def render(
    project_name: str,
    dependency_containers: list[DependencyContainer],
    rankdir: str,
    overlap: str,
    ratio: str,
    fontsize: str,
    dpi: str,
    shape: str,
    fontname: str,
    split_files: bool,
) -> None:
    if not os.path.exists("renders"):
        os.mkdir("renders")

    if split_files:
        _render_multiple_files(
            project_name=project_name,
            dependency_containers=dependency_containers,
            rankdir=rankdir,
            overlap=overlap,
            ratio=ratio,
            fontsize=fontsize,
            dpi=dpi,
            shape=shape,
            fontname=fontname,
        )
    else:
        _render_cluster_files(
            project_name=project_name,
            dependency_containers=dependency_containers,
            rankdir=rankdir,
            overlap=overlap,
            ratio=ratio,
            fontsize=fontsize,
            dpi=dpi,
            shape=shape,
            fontname=fontname,
        )


def _render_cluster_files(
    project_name: str,
    dependency_containers: list[DependencyContainer],
    rankdir: str,
    overlap: str,
    ratio: str,
    fontsize: str,
    dpi: str,
    shape: str,
    fontname: str,
) -> None:
    # Dirty hack to prevent a \t in the first edge
    edges = """
"""

    for dependency in dependency_containers:
        for _import in dependency.imports:
            basename = dependency.basename.rsplit(".", 1)[0]
            if _import["from_statement"] is not None:
                edges += f'\t"{basename}" -> "{_import["from_statement"]}";\n'

            from_statement = (
                _import["from_statement"]
                if _import["from_statement"]
                else basename
            )

            edges += '\t"{}" -> {{"{}"}};\n'.format(
                from_statement,
                '","'.join(_import["import_statements"]),
            )

    with open(f"renders/{project_name}.dot", mode="w") as file:
        file.write(
            DOT_TEMPLATE
            % (
                project_name,
                rankdir,
                overlap,
                ratio,
                fontsize,
                dpi,
                fontsize,
                shape,
                fontname,
                edges,
            ),
        )


def _render_multiple_files(
    project_name: str,
    dependency_containers: list[DependencyContainer],
    rankdir: str,
    overlap: str,
    ratio: str,
    fontsize: str,
    dpi: str,
    shape: str,
    fontname: str,
) -> None:
    for dependency in dependency_containers:
        # Dirty hack to prevent a \t in the first edge
        edges = """
"""
        for _import in dependency.imports:
            basename = dependency.basename.rsplit(".", 1)[0]
            if _import["from_statement"] is not None:
                edges += f'\t"{basename}" -> "{_import["from_statement"]}";\n'

            from_statement = (
                _import["from_statement"]
                if _import["from_statement"]
                else basename
            )

            edges += '\t"{}" -> {{"{}"}};\n'.format(
                from_statement,
                '", "'.join(_import["import_statements"]),
            )

        with open(f"renders/{basename}.dot", mode="w") as file:
            file.write(
                DOT_TEMPLATE
                % (
                    project_name,
                    rankdir,
                    overlap,
                    ratio,
                    fontsize,
                    dpi,
                    fontsize,
                    shape,
                    fontname,
                    edges,
                ),
            )
