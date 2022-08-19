from typing import Any, Dict, Optional

from myst.models import base_model


class HPOTrial(base_model.BaseModel):
    """Represents the result of a single HPO trial."""

    parameters: Dict[str, Any]
    metrics: Dict[str, Optional[float]]
    create_time: str
