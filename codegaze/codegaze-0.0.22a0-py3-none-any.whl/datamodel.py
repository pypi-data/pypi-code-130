# from dataclasses import dataclass
from dataclasses import field
from mimetypes import init
from typing import Optional
from pydantic.dataclasses import dataclass
import hashlib


@dataclass
class ExperimentConfig:
    """Configuration for a code generation experiment"""

    slug: str = field(default=None, init=True)
    name: str = "sample experiment"
    max_lines_per_block: int = 10
    description: str = "sample experiment"
    dataset: str = "humaneval"
    parser_retry: bool = True
    suffix: bool = False
    prompt_tokens: int = 1

    def __post_init__(self):
        field_strings = ", ".join(
            [f"{k}={v}" for k, v in self.__dict__.items() if k != "slug"]
        )
        self.slug = hashlib.sha1(field_strings.encode("utf-8")).hexdigest()


@dataclass
class ModelConfig:
    type: str  # "openai" or "huggingface"
    name: str
    description: str = "sample model"
    temperature: float = 0.2
    suffix: bool = False
    n_completions: int = 10
    path: str = "Salesforce/codegen-350M-multi"
    max_tokens: int = 300


@dataclass
class CompletionResult:
    text: str
    logprobs: Optional[list[float]]


@dataclass
class CodeBlock:
    """A code block extracted from a Code fragment or Function."""

    type: str
    """The type of the code block. This correspondes to a tree-sitter node type name."""

    text: str
    """The text of the code block."""

    h: int
    """The height index of the block in the fragment AST tree."""

    start_byte: int
    """The byte offset of the start of the code block in the fragment AST tree."""

    end_byte: int
    """The byte offset of the end of the code block in the fragment AST tree."""

    num_lines: int
    """The number of lines in the code block."""

    is_named: bool
    """Whether the code block is a named treesitter node."""

    child_count: int
    """The number of children of the code block."""

    parent_index: int
    """The index of the parent of the code block in the array serialized fragment AST tree."""

    block_index: int = 0
    """The index of the extracted block in function."""
