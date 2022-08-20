from typing import List, Text, Dict

import numpy as np
from pydantic import BaseModel


class ExistedUserAttributesVector(BaseModel):
    # NOTE record user with its corresponding factor, user_id's definition is
    # same as user_id used in model training.

    user_ids: List[Text]
    user_attributes_vector: List[np.ndarray]
    attribute_map_to_vector_position: Dict[Text, int]
    vector_position_map_to_attribute: Dict[int, Text]

    class Config:
        arbitrary_types_allowed = True
