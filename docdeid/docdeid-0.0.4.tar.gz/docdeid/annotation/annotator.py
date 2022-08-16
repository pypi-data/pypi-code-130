import re
from abc import ABC, abstractmethod

from docdeid.annotation.annotation import Annotation
from docdeid.document.document import Document


class BaseAnnotator(ABC):
    """
    An annotator annotates a text based on its internal logic and rules, and outputs a list of annotations.
    """

    @abstractmethod
    def annotate(self, document: Document):
        """Annotate the document."""


class LookupAnnotator(BaseAnnotator):
    """Annotate tokens based on a list of lookup values"""

    def __init__(self, lookup_values: list[str], category: str):
        self.lookup_values = lookup_values
        self.category = category
        super().__init__()

    def annotate(self, document: Document):
        tokens = document.tokens

        document.add_annotations(
            [
                Annotation(
                    text=token.text,
                    start_char=token.start_char,
                    end_char=token.end_char,
                    category=self.category,
                )
                for token in tokens
                if token.text in self.lookup_values
            ]
        )


class RegexpAnnotator(BaseAnnotator):
    """Annotate text based on regular expressions"""

    def __init__(self, regexp_pattern: str, category: str):
        self.regexp_pattern = regexp_pattern
        self.category = category
        super().__init__()

    def annotate(self, document: Document):
        document.add_annotations(
            [
                Annotation(match.group(0), match.start(), match.end(), self.category)
                for match in re.finditer(self.regexp_pattern, document.text)
            ]
        )


class MetaDataAnnotator(BaseAnnotator):
    """A simple annotator that check the metadata (mainly testing)."""

    def __init__(self, category: str):
        self.category = category
        super().__init__()

    def annotate(self, document: Document):

        for token in document.tokens:
            if token.text == document.get_meta_data_item("forbidden_string"):
                document.add_annotation(
                    Annotation(
                        token.text, token.start_char, token.end_char, self.category
                    )
                )
