# ----------------------------------------------------------------------------------------------------# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021, 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class Subscription():

    def __init__(self, subscription):
        subscription = subscription or {}

        # Data sources
        self.explain_queue_ds = DataSource(subscription.get("explain_queue_ds", {}))
        self.explain_result_ds = DataSource(subscription.get("explain_result_ds", {}))
        self.payload_ds = DataSource(subscription.get("payload_data_source", {}))

        # Subscription details
        self.data_mart_id = subscription.get("data_mart_id")
        self.subscription_id = subscription.get("subscription_id")
        self.binding_id = subscription.get("binding_id")

        asset = subscription.get("asset") or {}
        self.asset_name = asset.get("name")
        self.asset_id = asset.get("id")

        deployment = subscription.get("deployment") or {}
        self.deployment_name = deployment.get("name")
        self.deployment_id = deployment.get("id")

        self.scoring_id_column = subscription.get("scoring_id_column")
        self.scoring_timestamp_column = subscription.get(
            "scoring_timestamp_column")

class DataSource():
    """Class representing datasource"""

    def __init__(self, data_source):
        self.connection = data_source.get("connection", {})
        self.credentials = data_source.get("credentials", {})
        self.connection_type = self.connection.get("type")
        self.database = data_source.get("database_name")
        self.schema = data_source.get("schema_name")
        self.table = data_source.get("table_name")
        self.partition_column = data_source.get("partition_column")
        self.num_partitions = data_source.get("num_partitions")

    def __str__(self):
        ds_dict = vars(self).copy()
        del ds_dict["connection"]
        del ds_dict["credentials"]
        return str(ds_dict)