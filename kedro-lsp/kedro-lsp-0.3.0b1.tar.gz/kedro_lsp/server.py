"""Kedro Language Server."""
import logging
import re
from pathlib import Path
from typing import List, Optional

import yaml
from kedro.framework.project import settings
from kedro.framework.startup import ProjectMetadata, bootstrap_project
from pygls.lsp.methods import DEFINITION
from pygls.lsp.types import Location, Position, Range, TextDocumentPositionParams
from pygls.protocol import LanguageServerProtocol
from pygls.server import LanguageServer
from pygls.workspace import Document
from yaml.loader import SafeLoader

RE_START_WORD = re.compile("[A-Za-z_0-9:]*$")
RE_END_WORD = re.compile("^[A-Za-z_0-9:]*")


try:
    from kedro.config.config import _path_lookup
except ImportError:
    ...


def split_dict(d: dict):
    return "  - " + "\n  - ".join([f"{k}: {v}" for k, v in d.items()])


class KedroLanguageServer(LanguageServer):
    """Store Kedro-specific information in the language server."""

    @property
    def project_metadata(self):
        if hasattr(self, "_project_metadata"):
            return self._project_metadata

        project_metadata = bootstrap_project(Path.cwd())
        self._project_metadata = project_metadata
        return self._project_metadata

    @property
    def settings(self):
        if hasattr(self, "_settings"):
            return self._settings

        self.project_metadata

        self._settings = settings
        return settings


SERVER = KedroLanguageServer(protocol_cls=LanguageServerProtocol)


class SafeLineLoader(SafeLoader):  # pylint: disable=too-many-ancestors
    """A YAML loader that annotates loaded nodes with line number."""

    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        mapping["__line__"] = node.start_mark.line
        return mapping


def _word_at_position(position: Position, document: Document) -> str:
    """Get the word under the cursor returning the start and end positions."""
    if position.line >= len(document.lines):
        return ""

    line = document.lines[position.line]
    i = position.character
    # Split word in two
    start = line[:i]
    end = line[i:]

    # Take end of start and start of end to find word
    # These are guaranteed to match, even if they match the empty string
    m_start = RE_START_WORD.findall(start)
    m_end = RE_END_WORD.findall(end)

    return m_start[0] + m_end[-1]


def _get_param_location(
    project_metadata: ProjectMetadata, word: str
) -> Optional[Location]:
    param = word.split("params:")[-1]
    parameters_path = project_metadata.project_path / "conf" / "base" / "parameters.yml"
    # TODO: cache -- we shouldn't have to re-read the file on every request
    parameters_file = open(parameters_path, "r")
    param_line_no = None
    for line_no, line in enumerate(parameters_file, 1):
        if line.startswith(param):
            param_line_no = line_no
            break
    parameters_file.close()

    if param_line_no is None:
        return None

    location = Location(
        uri=f"file://{parameters_path}",
        range=Range(
            start=Position(line=param_line_no - 1, character=0),
            end=Position(
                line=param_line_no,
                character=0,
            ),
        ),
    )
    return location


def _eighteen_path_lookup(server):
    from kedro.config.common import _lookup_config_filepaths

    conf_loader = server.settings.CONFIG_LOADER_CLASS(server.settings.CONF_SOURCE)
    paths = []
    for path in conf_loader.conf_paths:
        paths.extend(
            _lookup_config_filepaths(
                conf_path=Path(path),
                patterns=["catalog*", "**/catalog*/**", "**/catalog*"],
                processed_files=set(),
                logger=None,
            )
        )
    return paths


@SERVER.feature(DEFINITION)
def definition(
    server: KedroLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    """Support Goto Definition for a dataset or parameter.
    Currently only support catalog defined in `conf/base`
    """

    document = server.workspace.get_document(params.text_document.uri)
    word = _word_at_position(params.position, document)

    if word.startswith("params:"):
        param_location = _get_param_location(server.project_metadata, word)
        if param_location:
            return [param_location]

    try:
        catalog_paths = _path_lookup(
            conf_path=server.project_metadata.project_path / server.settings.CONF_ROOT,
            patterns=["catalog*", "**/catalog*/**", "**/catalog*"],
        )
    except NameError:
        catalog_paths = _eighteen_path_lookup(server)

    locations = []

    for catalog_path in catalog_paths:
        catalog_conf = yaml.load(catalog_path.read_text(), Loader=SafeLineLoader)

        if word in catalog_conf:
            line = catalog_conf[word]["__line__"]
            location = Location(
                uri=f"file://{catalog_path}",
                range=Range(
                    start=Position(line=line - 1, character=0),
                    end=Position(
                        line=line,
                        character=0,
                    ),
                ),
            )
            locations.append(location)

    return locations or None


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2087)
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    print("starting on {host}:{port}")
    SERVER.start_tcp(args.host, args.port)
