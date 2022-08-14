from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel, ValidationError

from scoringmodel.config.core import config


def drop_na_inputs(*, input_data: pd.DataFrame) -> pd.DataFrame:
    """Check model inputs for na values and filter."""
    validated_data = input_data.copy()
    new_vars_with_na = [
        var
        for var in config.model_config.input_columns
        if validated_data[var].isnull().sum() > 0
    ]
    validated_data.dropna(subset=new_vars_with_na, inplace=True)

    return validated_data

def validate_inputs(*, input_data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[dict]]:
    """Check model inputs for unprocessable values."""

    # convert syntax error field names (beginning with numbers)
    input_data.rename(columns=config.model_config.variables_to_rename, inplace=True)
    relevant_data = input_data[config.model_config.input_columns].copy()
    validated_data = drop_na_inputs(input_data=relevant_data)
    errors = None

    try:
        # replace numpy nans so that pydantic can validate
        MultipleCreditDataInputs(
            inputs=validated_data.replace({np.nan: None}).to_dict(orient="records")
        )
    except ValidationError as error:
        errors = error.json()

    return validated_data, errors

class CreditDataInputSchema(BaseModel):
    limit_bal: Optional[int]
    sex: Optional[int]
    education: Optional[int]
    marriage: Optional[int]
    age: Optional[int]
    pay_1: Optional[int]
    pay_2: Optional[int]
    pay_3: Optional[int]
    pay_4: Optional[int]
    pay_5: Optional[int]
    pay_6: Optional[int]
    bill_amt1: Optional[int]
    bill_amt2: Optional[int]
    bill_amt3: Optional[int]
    bill_amt4: Optional[int]
    bill_amt5: Optional[int]
    bill_amt6: Optional[int]
    pay_amt1: Optional[int]
    pay_amt2: Optional[int]
    pay_amt3: Optional[int]
    pay_amt4: Optional[int]
    pay_amt5: Optional[int]
    pay_amt6: Optional[int]


class MultipleCreditDataInputs(BaseModel):
    inputs: List[CreditDataInputSchema]