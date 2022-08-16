# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import base64
import uuid
import json
from math import isnan
from decimal import Decimal
import pandas as pd
from collections import OrderedDict

try:
    from pyspark.sql import Row
except ImportError as e:
    pass

from ibm_wos_utils.explainability.explainers.explainer import Explainer
from ibm_wos_utils.explainability.entity.constants import Status
from ibm_wos_utils.explainability.entity.explain_response import Error, ErrorTarget, ErrorSchema
from ibm_wos_utils.explainability.entity.constants import ProblemType
from ibm_wos_utils.explainability.utils.date_time_util import DateTimeUtil


class ComputeExplanation():

    def __init__(self, explain_config, subscription, score_response, explanations_counter=None, created_by="openscale", columns=None, chunk_size=None):
        self.explain_config = explain_config
        self.columns = columns
        self.subscription = subscription
        self.score_response = score_response
        self.created_by = created_by
        self.prediction = None
        self.probability = None
        self.explanations_counter = explanations_counter
        self.chunk_size = chunk_size

    def compute(self, data):
        explainer = Explainer(self.explain_config)
        sc = self.score_response.value.copy()
        from more_itertools import ichunked
        chunks = ichunked(data, self.chunk_size)
        for chunk in chunks:
            df = pd.DataFrame(chunk, columns=self.columns)
            explanations = explainer.explain(
                df, scoring_response=sc)
            df["explanations"] = explanations[0]

            for _, row in df.iterrows():
                created_at = DateTimeUtil.get_current_datetime()
                yield self.get_response_row(row, created_at)

    def get_response_row(self, row, created_at):

        explanations = [row["explanations"]]
        status = Status.ERROR if all(
            e.get("error") for e in explanations) else Status.FINISHED
        scoring_id = row[self.subscription.scoring_id_column]
        if self.explanations_counter:
            counter_dict = {
                "failed": 1 if status is Status.ERROR else 0,
                "total": 1,
                "failed_scoring_ids": [scoring_id] if status is Status.ERROR else []
            }
            self.explanations_counter.add(counter_dict)

        errors = []
        for e in explanations:
            if e.get("error"):
                errors.append(e.get("error"))
                del e["error"]

        return Row(asset_name=self.subscription.asset_name,
                   binding_id=self.subscription.binding_id,
                   created_at=created_at,
                   created_by=self.created_by,
                   data_mart_id=self.subscription.data_mart_id,
                   deployment_id=self.subscription.deployment_id,
                   deployment_name=self.subscription.deployment_name,
                   error=bytearray(base64.b64encode(json.dumps(errors).encode(
                       "utf-8"))) if errors else None,
                   explanation=self.__encode_explanations(row, explanations),
                   explanation_input=None,
                   explanation_output=None,
                   explanation_type=self.explain_config.explanation_types[0].value,
                   finished_at=DateTimeUtil.get_current_datetime(),
                   object_hash=self.__get_object_hash(row),
                   prediction=row[self.explain_config.prediction_column],
                   probability=max(row[self.explain_config.probability_column]
                                   ) if self.explain_config.probability_column in row else None,
                   request_id=row["explanation_task_id"] if "explanation_task_id" in row else str(
                       uuid.uuid4()),
                   scoring_id=scoring_id,
                   status=status.name,
                   subscription_id=self.subscription.subscription_id)

    def compute_no_record_explanation(self, data):
        entity = {"entity": {
            "asset": {
                "id": self.subscription.asset_id,
                "name": self.subscription.asset_name,
                "problem_type": self.explain_config.problem_type.value,
                "input_data_type": self.explain_config.input_data_type.value,
                "deployment": {
                    "id": self.subscription.deployment_id,
                    "name": self.subscription.deployment_name
                }
            }
        }}
        explanation = bytearray(base64.b64encode(
            json.dumps(entity).encode("utf-8")))
        for d in data:
            yield self.get_no_record_response(d, explanation)

    def get_no_record_response(self, row, explanation):
        time_stamp = DateTimeUtil.get_current_datetime()
        vals = [row[self.subscription.scoring_id_column]]
        error = Error(code="AIQES6010E",
                      message="Could not find an input data row in the payload logging table for the {0} transaction id".format(
                          *vals),
                      target=ErrorTarget(
                          "field", self.explain_config.explanation_types[0].value),
                      vals=vals)
        errors = [ErrorSchema().dump(error)]

        return Row(asset_name=self.subscription.asset_name,
                   binding_id=self.subscription.binding_id,
                   created_at=time_stamp,
                   created_by=self.created_by,
                   data_mart_id=self.subscription.data_mart_id,
                   deployment_id=self.subscription.deployment_id,
                   deployment_name=self.subscription.deployment_name,
                   error=bytearray(base64.b64encode(
                       json.dumps(errors).encode("utf-8"))),
                   explanation=explanation,
                   explanation_input=None,
                   explanation_output=None,
                   explanation_type=self.explain_config.explanation_types[0].value,
                   finished_at=time_stamp,
                   object_hash=None,
                   prediction=None,
                   probability=None,
                   request_id=row["explanation_task_id"],
                   scoring_id=row[self.subscription.scoring_id_column],
                   status=Status.ERROR.name,
                   subscription_id=self.subscription.subscription_id)

    def __encode_explanations(self, row, explanations):
        input_features = []
        for f in self.explain_config.feature_columns:
            val = row[f]
            if f in self.explain_config.categorical_columns:
                ftype = "categorical"
            else:
                ftype = "numerical"
                val = None if val is None or isnan(val) else val

            input_features.append({"name": f,
                                   "value": float(val) if isinstance(val, Decimal) else val,
                                   "feature_type": ftype})

        entity = {"entity": {
            "asset": {
                "id": self.subscription.asset_id,
                "name": self.subscription.asset_name,
                "problem_type": self.explain_config.problem_type.value,
                "input_data_type": self.explain_config.input_data_type.value,
                "deployment": {
                    "id": self.subscription.deployment_id,
                    "name": self.subscription.deployment_name
                }
            },
            "input_features": input_features,
            "explanations": explanations
        }}
        return bytearray(base64.b64encode(json.dumps(entity).encode("utf-8")))

    def __get_object_hash(self, row):
        feature_values = {f: row[f]
                          for f in self.explain_config.feature_columns}

        feature_values_sorted = OrderedDict(
            sorted(feature_values.items()))
        # convert the dict to a single row rectangular dataframe and get hash for first row
        feature_row_df = pd.DataFrame(feature_values_sorted, index=[0])
        return str(abs(pd.util.hash_pandas_object(
            feature_row_df, encoding="utf8").iloc[0]))
