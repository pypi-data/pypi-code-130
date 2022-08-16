
from codegaze import CodeBlockParser, TreeSitterParser
from codegaze import OpenAICodeGenerator as codegen
import pytest


@pytest.fixture
def code_string():
    return '''import requests
def get_ip():
    """Get my current external IP.
    Other line.
    """
    result = requests.get("https://icanhazip.com").text.strip()
    return result
'''


def test_tree_sitter_parser(code_string):
    language = "python"
    tree_sitter_parser = TreeSitterParser(language=language)
    assert language in tree_sitter_parser.list_languages()


def test_block_parser(code_string):
    tree_sitter_parser = TreeSitterParser(language="python")
    code_parser = CodeBlockParser(tree_sitter_parser.parser)
    blocks = code_parser.extract_blocks(code_string)
    nodes = code_parser.walk(code_string)
    assert len(blocks) == 2
    assert len(nodes) == 44
    assert blocks[0].text == "import requests"
