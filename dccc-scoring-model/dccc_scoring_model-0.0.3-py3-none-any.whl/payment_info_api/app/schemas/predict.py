from typing import Any, List, Optional

from pydantic import BaseModel
from scoringmodel.processing.validation import CreditDataInputSchema


class PredictionResults(BaseModel):
    errors: Optional[Any]
    version: str
    predictions: Optional[List[float]]


class MultipleCreditDataInputs(BaseModel):
    inputs: List[CreditDataInputSchema]

    class Config:
        schema_extra = {
            "example": {
                "inputs": [
                    {
                     "limit_bal": 200000,
                     "sex": 1,
                     "education": 2,
                     "marriage": 1,
                     "age": 32,
                     "pay_1": 0,
                     "pay_2": 0,
                     "pay_3": 0,
                     "pay_4": 0,
                     "pay_5": 0,
                     "pay_6": 0,
                     "bill_amt1": 24954,
                     "bill_amt2": 29859,
                     "bill_amt3": 43813,
                     "bill_amt4": 35355,
                     "bill_amt5": 32113,
                     "bill_amt6": 30876,
                     "pay_amt1": 29859,
                     "pay_amt2": 43813,
                     "pay_amt3": 35355,
                     "pay_amt4": 32113,
                     "pay_amt5": 30876,
                     "pay_amt6": 23562,
                    }
                ]
            }
        }