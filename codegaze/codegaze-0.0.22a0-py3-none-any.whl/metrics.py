from abc import abstractmethod
from typing import Union
import Levenshtein
import torch

from codegaze import CodeBlockParser
from transformers import AutoTokenizer, AutoModel

# from tokenizers import Tokenizer 
import logging

logger = logging.getLogger(__name__)


class Metric(object):
    @abstractmethod
    def __init__(self):
        """initialize the metric"""

    @abstractmethod
    def compute(self, a: Union[list[str], str], b: Union[list[str], str]) -> float:
        """Compute distance"""


class EditMetric(Metric):
    def compute(self, a: Union[list[str], str], b: Union[list[str], str]) -> float:
        """Compute the relative edit similarity between two strings

        Args:
            a (Union[list[str], str]): string a
            b (Union[list[str], str]): string b

        Returns:
            float: relative edit distance
        """
        assert isinstance(a, str) or isinstance(
            a, list
        ), "a must be a string or a list of strings " "but got {}".format(
            type(a)
        )  # type: ignore
        assert isinstance(b, str) or isinstance(
            b, list
        ), "b must be a string or a list of strings " "but got {}".format(
            type(b)
        )  # type: ignore

        distance = Levenshtein.distance(a, b)
        max_val = max(len(a), len(b))
        rel_distance: float = distance / max_val if max_val > 0 else 0
        return 1 - rel_distance


class JaroWinklerMetric(Metric):
    def compute(self, a: Union[list[str], str], b: Union[list[str], str]) -> float:
        """Compute the Jaro-Winkler similarity between two strings

        Args:
            a (Union[list[str], str]): string a
            b (Union[list[str], str]): string b

        Returns:
            float: Jaro-Winkler distance
        """
        assert isinstance(a, str) or isinstance(
            a, list
        ), "a must be a string or a list of strings " "but got {}".format(
            type(a)
        )  # type: ignore
        assert isinstance(b, str) or isinstance(
            b, list
        ), "b must be a string or a list of strings " "but got {}".format(
            type(b)
        )  # type: ignore

        jw_distance = 1 - Levenshtein.jaro_winkler(a, b)
        return 1 - jw_distance


class ASTMetric(Metric):
    def __init__(self, parser: CodeBlockParser):
        assert isinstance(parser, CodeBlockParser), "parser must be a CodeBlockParser"
        self.parser = parser

    def get_nodes(self, s: str, max_lines_per_block: int = 1) -> list[str]:
        """Serialize code string to list of node types
        Args:
            s (str): code string
            max_lines_per_block (int, optional): max number of lines
            per block. Defaults to 1 to get each node in the tree.
        Returns:
        """
        nodes = self.parser.extract_blocks(
            s, max_lines_per_block=max_lines_per_block, skip_parent_block=False
        )
        node_types = [node.type for node in nodes]
        return node_types

    def compute(self, a: str, b: str, max_lines_per_block: int = 1) -> float:
        n1 = self.get_nodes(a, max_lines_per_block)
        n2 = self.get_nodes(b, max_lines_per_block)
        edit_metric = EditMetric()
        return edit_metric.compute(n1, n2)


class NeuralMetric(Metric):
    def __init__(self, hfmodel: str = "microsoft/codebert-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(hfmodel)
        self.model = AutoModel.from_pretrained(hfmodel)
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        self.cos = torch.nn.CosineSimilarity(dim=0, eps=1e-6)

    def compute(self, a: str, b: str) -> float:
        tokenized_code = self.tokenizer(
            [a, b], padding=True, truncation=True, return_tensors="pt"
        ).to(self.device)
        encoded_code = self.model(tokenized_code.input_ids)["last_hidden_state"]
        emb_a = encoded_code[0].mean(dim=0) 
        emb_b = encoded_code[1].mean(dim=0) 
        return float(self.cos(emb_a, emb_b).item())
