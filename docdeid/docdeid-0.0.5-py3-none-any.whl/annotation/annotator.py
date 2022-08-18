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

    def __init__(self, regexp_patterns: list[re.Pattern], category: str, capturing_group: int = 0, ):
        self.regexp_patterns = regexp_patterns
        self.category = category
        self.capturing_group = capturing_group
        super().__init__()

    def annotate(self, document: Document):

        for regexp_pattern in self.regexp_patterns:

            for match in regexp_pattern.finditer(document.text):

                text = match.group(self.capturing_group)
                start, end = match.span(self.capturing_group)

                document.add_annotation(Annotation(text, start, end, self.category))


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
