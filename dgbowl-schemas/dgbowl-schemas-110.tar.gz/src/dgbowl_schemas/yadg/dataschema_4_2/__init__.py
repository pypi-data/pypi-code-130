from pydantic import BaseModel, Extra
from typing import Sequence
from .metadata import Metadata
from .step import Steps


class DataSchema(BaseModel, extra=Extra.forbid):
    metadata: Metadata
    """Metadata information for yadg."""

    steps: Sequence[Steps]
    """A sequence of parser steps."""
