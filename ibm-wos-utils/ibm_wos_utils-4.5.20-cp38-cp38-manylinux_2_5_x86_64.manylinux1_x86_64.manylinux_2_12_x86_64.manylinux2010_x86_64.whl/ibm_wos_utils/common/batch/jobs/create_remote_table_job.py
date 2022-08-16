# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import collections
import json
try:
    from pyspark.sql import SQLContext
except ImportError as e:
    pass
from ibm_wos_utils.joblib.jobs.aios_spark_job import AIOSBaseJob
from ibm_wos_utils.joblib.utils import ddl_utils
from ibm_wos_utils.joblib.utils.constants import *
from ibm_wos_utils.joblib.utils.db_utils import DbUtils
from ibm_wos_utils.joblib.utils.joblib_utils import JoblibUtils
from ibm_wos_utils.joblib.utils.param_utils import get
from ibm_wos_utils.joblib.utils.jdbc_utils import JDBCUtils



class CreateRemoteTableJob(AIOSBaseJob):
    """Spark job to get the explanations from hive"""

    def run_job(self):
        self.logger.info("Starting the table creation job")
        self.logger.info(self.arguments)
        is_error = False
        error_json = {
                "error": []
            }
        try:
            tables = get(self.arguments, "tables")
            tables_status = []
            table_info_details = []
            table_info_json = {}
            jdbc_connection_details = {}
            credentials_set = False

            for table in tables:
                table_status = {
                    "table_name": get(table, "table_name")
                }
                try:
                    failure = None
                    database_name = get(table, "database_name")
                    schema_name = get(table, "schema_name")
                    table_name = get(table, "table_name")

                    schema = get(table, "schema")
                    auto_create = get(table, "auto_create")
                    table_parameters = get(table, "parameters")
                    if not table_parameters:
                        table_parameters = {}
                    partition_column = get(table_parameters, "partition_column") \
                        if self.storage_type == StorageType.JDBC.value else None

                    if auto_create:
                        if self.storage_type == StorageType.HIVE.value:
                            sql_context = SQLContext(self.sc)

                            if table_name in sql_context.tableNames(database_name):
                                msg = "Autocreate is set to True. However, a table with the name {} already exists in the database {}.".format(
                                        table_name, database_name)
                                raise Exception(msg)
                            
                            hive_storage_format = "csv"
                            if table_parameters:
                                hive_storage_format = get(table_parameters, "hive_storage_format") or "csv"
                            table_format = hive_storage_format.lower()

                            create_table_ddl = ddl_utils.generate_table_ddl_batch_simplification(
                                schema=schema,
                                database_name=database_name,
                                table_name=table_name,
                                stored_as=table_format)
                            self.logger.info("Creating table with DDL: {}".format(create_table_ddl.rstrip(";")))
                            self.spark.sql(create_table_ddl.rstrip(";"))

                        elif self.storage_type == StorageType.JDBC.value or (
                            self.location_type is not None and self.location_type == LocationType.JDBC.value):

                            probability_column = JoblibUtils.get_column_by_modeling_role(
                                            get(table, "schema"), 'probability')

                            util_instance = JDBCUtils.get_util_instance(
                                spark=self.spark,
                                database_name=database_name,
                                table_name=table_name,
                                schema_name=schema_name,
                                connection_properties=self.jdbc_connection_properties,
                                sql_query=None,
                                probability_column=probability_column)

                            if util_instance.check_if_table_exists():
                                msg = "Autocreate is set to True. However, a table with the name {} already exists in the database {}.".format(
                                        table_name, database_name)
                                raise Exception(msg)

                            partition_column = get(table_parameters, "partition_column")
                            index_columns = get(table_parameters, "index_columns") or []
                            primary_keys = get(table_parameters, "primary_keys") or []
                            max_length_categories = get(table_parameters, "max_length_categories") or {}

                            create_table_column_types, \
                                table_info_json, \
                                    partition_column_in_schema = self.convert_data_types(
                                        schema=schema,
                                        schema_name=schema_name,
                                        table_name=table_name,
                                        partition_column=partition_column,
                                        max_length_categories=max_length_categories,
                                        index_columns=index_columns,
                                        primary_keys=primary_keys)

                            # add this only if user has specified a partition column and its not part of schema
                            # skip in case user has either not specified partition column or 
                            # has specified it, but its part of schema.
                            if partition_column and not partition_column_in_schema:
                                # If partition column is not already present in the schema, 
                                # add it to the schema as a non-nullable field
                                partition_field = self.__get_partition_column_field(partition_column)
                                schema["fields"].append(partition_field)

                            if not credentials_set:
                                jdbc_connection_details = self.jdbc_connection_properties
                                jdbc_connection_details["certificate"] = get(self.arguments, "storage.connection.certificate")
                                credentials_set = True

                            emptyRDD = self.sc.emptyRDD()
                        
                            from pyspark.sql.types import StructType
                            # Restore schema from json:
                            new_schema = StructType.fromJson(schema)
                            self.logger.info("schema after converting to db2 types {}".format(new_schema))

                            spark_df = emptyRDD.toDF(new_schema)
                            JDBCUtils.write_dataframe_to_table(
                                spark_df=spark_df,
                                mode="overwrite",
                                database_name=database_name,
                                table_name=table_name,
                                schema_name=schema_name,
                                connection_properties=self.jdbc_connection_properties,
                                probability_column=probability_column,
                                create_table_column_types=create_table_column_types)

                            self.logger.info("created table {}.{} in db2".format(schema_name, table_name))
                    else:
                        self.logger.info("Auto create is set to False for the table {}. Hence, validating the table.".format(table_name))
                        self.validate_table(database_name, table_name, schema_name, table, partition_column)
                            
                    table_status["state"] = "active"
                except Exception as e:
                    is_error = True
                    error_json["error"].append(str(e))
                    failure = {
                                "errors": [
                                    {
                                        "message": str(e)
                                    }
                                ]
                            }
                    table_status["failure"] = json.dumps(failure)
                    table_status["state"] = "error"
                    self.logger.exception("An error occured while creating table. Reason: {}".format(str(e)))
                finally:
                    tables_status.append(table_status)
                    if table_info_json:
                        table_info_details.append(table_info_json)
            if is_error:
                raise Exception("Create Table(s) job failed. Reason: {}".format(error_json))
            self.logger.info(
                "Completed table creation job")
        except Exception as ex:
            self.logger.exception(str(ex))
            super().save_exception_trace(str(ex))
            raise ex
        finally:
            self.save_data(self.arguments.get("output_file_path") +
                            "/tables_status.json", {"tables_status":tables_status})

            table_info_json = {}
            if table_info_details:
                table_info_json["table_info_details"] = json.dumps(table_info_details)
            if jdbc_connection_details:
                table_info_json["jdbc_connection_details"] = jdbc_connection_details
                    
            self.logger.info("table info json {}".format(table_info_json))

            if table_info_json:
                self.save_data(self.arguments.get("output_file_path") +
                            "/table_info.json", table_info_json)

    def convert_data_types(
        self, schema, schema_name, table_name, partition_column,
        max_length_categories, index_columns, primary_keys):

        spark_to_db2_map = {
            "boolean": "boolean",
            "byte": "bigint",
            "short": "bigint",
            "integer": "bigint",
            "long": "bigint",
            "float": "double",
            "double": "double",
            "timestamp": "timestamp",
            "string": "varchar",
            "binary": "blob"
        }

        column_string = ""
        table_info_json = {}
        partition_column_in_schema = False
        primary_key = None
        index_column = None

        get_varchar_length = lambda x: max(64, get(max_length_categories, x, 32)*2)
        ddl_fields = schema.get("fields").copy()
        for field in ddl_fields:
            feature_name = get(field, "name")
            feature_type = get(field, "type")

            if isinstance(feature_type, dict):
                feature_type = "varchar"
            else:
                db2_element_type = spark_to_db2_map.get(feature_type)
                if db2_element_type is not None:
                    feature_type = db2_element_type

            if feature_type == "blob":
                continue

            if feature_type == "varchar":
                if get(field, "metadata.modeling_role") == "probability":
                    feature_type += "(32000)"
                else:
                    # check if field has length
                    feature_length = get(field, "length")
                    if not feature_length:
                        # fall back
                        feature_length = get(field, "metadata.columnInfo.columnLength")

                    if not feature_length:
                        # default option
                        feature_length = get_varchar_length(feature_name)
                    feature_type += "({})".format(feature_length) 

            if get(field, "metadata.modeling_role") == "record-id":
                primary_key = feature_name
            
            if get(field, "metadata.modeling_role") == "record-timestamp":
                index_column = feature_name

            # If the partition column is already present in the schema 
            # validate it to be a numeric or time stamp column and do 
            # not alter the db2 table with the partition column
            if feature_name == partition_column:
                partition_column_in_schema = True
                if feature_type not in ["bigint", "timestamp", "double"]:
                    raise Exception("partition column should either be a numeric or timestamp column.")

            column_string += "`{}` {}, ".format(feature_name, feature_type.upper())
        column_string = column_string.rstrip()
        
        table_info_json = self.__get_table_info_json(
            schema_name=schema_name,
            table_name=table_name,
            partition_column=partition_column,
            primary_key=primary_key,
            index_column=index_column, 
            partition_column_in_schema=partition_column_in_schema,
            additional_index_columns=index_columns,
            additional_primary_keys=primary_keys)
            
        self.logger.info("column string {}".format(column_string.rstrip(",")))
        return column_string.rstrip(","), table_info_json, partition_column_in_schema

    def __get_table_info_json(
        self, schema_name, table_name,
        partition_column, primary_key, index_column,
        partition_column_in_schema,
        additional_index_columns, additional_primary_keys):
        
        table_info_json = {}
        table_info_json["schema_name"] = schema_name
        table_info_json["table_name"] = table_name
        
        if partition_column and not partition_column_in_schema:
            table_info_json["partition_column"] = partition_column
        
        if primary_key:
            table_info_json["primary_key"] = primary_key
        
        if index_column:
            table_info_json["index_column"] = index_column
        
        if additional_index_columns:
            table_info_json["additional_index_columns"] = additional_index_columns

        if additional_primary_keys:
            table_info_json["additional_primary_keys"] = additional_primary_keys
        
        return table_info_json

    def __get_partition_column_field(self, partition_column):
        partition_field = {
            "name": partition_column,
            "type": "long",
            "nullable": False,
            "metadata": {
                "modeling_role": "partition-column"
            }
        }
        return partition_field

    def validate_table(self, database_name, table_name, schema_name, table, partition_column=None):

        map_data_types = True
        # Mapping between Hive and Spark data types. Datatypes like "map", "array" which are present in both
        # Hive and Spark are not part of the mapping below. Hive data type is used in that case.
        # Reference:
        # https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.4/integrating-hive/content/hive_hivewarehouseconnector_supported_types.html
        hive_to_spark_map = {
            "tinyint": "byte",
            "smallint": "short",
            "integer": "integer",
            "int": "integer",
            "bigint": "long",
            "float": "float",
            "double": "double",
            "decimal": "decimal",
            "string": "string",
            "varchar": "string",
            "binary": "binary",
            "boolean": "boolean",
            "interval": "calendarinterval"
        
        }
        probability_column = JoblibUtils.get_column_by_modeling_role(
                    get(table, "schema"), 'probability')
        columns = DbUtils.list_columns(
                    self.spark, self.location_type,
                    database_name, table_name,
                    schema_name=schema_name, connection_properties=self.jdbc_connection_properties,
                    probability_column=probability_column)

        actual_schema = {}

        is_error_local = False
        is_error = False
        error_json = {
                "error": []
            }

        try:
            for column in columns:
                if map_data_types:
                    data_type = get(
                            hive_to_spark_map, column.dataType.lower())
                    if data_type is None:
                        data_type = column.dataType.lower()

                        # For hive datatype of format like: array<int>, fetch the inner datatype and convert it
                        # Complex datatypes like array, map are present in
                        # both hive and spark
                        type_split = data_type.split("<")
                        if len(type_split) > 1:
                            type_split_0 = type_split[0]
                            type_split_1 = type_split[1][:-1]
                            spark_sub_type = get(
                                hive_to_spark_map, type_split_1)
                            if spark_sub_type is not None:
                                data_type = "{}<{}>".format(
                                    type_split_0, spark_sub_type)

                    actual_schema[column.name.lower()] = data_type
                else:
                    actual_schema[column.name.lower(
                    )] = column.dataType.lower()

            # validate table schema
            # iterate through expected column names and verify they exist in target table
            # we are verifying expected list, its okay for target table to
            # have a lot more columns than expectation
            self.logger.info("Validating schema...")
            expected_columns = get(table, "schema")
            self.logger.info(
                "Expected columns : {}".format(expected_columns))
            self.logger.info("Actual Schema: {}".format(actual_schema))

            columns_not_found = []
            expected_val_not_present = []
            data_type_mismatch = []

            for column in get(expected_columns, "fields"):
                if get(column, "metadata.deleted") is True:
                    # skip validation if this column has metadata with deleted set to true
                    continue

                key = get(column, "name")
                value = get(column, "type")

                # column name validation
                if not key or key.lower() not in actual_schema.keys():
                    is_error = True
                    is_error_local = True
                    columns_not_found.append(key)
                    continue

                if value is None:
                    # Unlikely to happen
                    is_error = True
                    is_error_local = True
                    expected_val_not_present.append(key)
                    continue

                valid_values = []
                integrals = ["short", "integer", "long"]
                fractions = ["float", "double", "decimal"]

                if isinstance(value, collections.Mapping):
                    # for columns with the type stored in a dictionary,
                    # prepare column type as a string
                    data_type = value.get("type").lower()
                    element_type = value.get("elementType").lower()
                    if element_type.lower() in integrals:
                        valid_values = list(
                            map(lambda t: "{}<{}>".format(data_type, t), integrals))
                    elif element_type.lower() in fractions:
                        valid_values = list(
                            map(lambda t: "{}<{}>".format(data_type, t), fractions))
                    else:
                        valid_values = [
                            "{}<{}>".format(
                                data_type, element_type)]
                elif value.lower() in integrals:
                    valid_values = integrals
                elif value.lower() in fractions:
                    valid_values = fractions
                else:
                    valid_values = [value.lower()]

                data_type_dict = dict()
                # column name found, validate column datatype
                if str(actual_schema[key.lower()]) not in valid_values:
                    is_error = True
                    is_error_local = True
                    data_type_dict["column_name"] = key
                    data_type_dict["expected_type"] = valid_values
                    data_type_dict["actual_type"] = actual_schema.get(
                        key.lower())
                    data_type_mismatch.append(data_type_dict)

            # partition column name validation
            if partition_column and partition_column not in actual_schema.keys():
                is_error = True
                is_error_local = True
                columns_not_found.append(partition_column)

            # Prepare error_json
            error_string = "database_name: `{}`, table_name: `{}`;".format(
                database_name, table_name)
            if len(columns_not_found) != 0:
                error_string += " Column(s) not found: {};".format(
                    columns_not_found)
            if len(expected_val_not_present) != 0:
                error_string += " No expected value present for column(s): {};".format(
                    expected_val_not_present)
            if len(data_type_mismatch) != 0:
                error_string += " Datatype mismatch for column(s): {}".format(
                    data_type_mismatch)

            if is_error_local:
                error_json["error"].append({
                    "database": database_name,
                    "table": table_name,
                    "error": error_string
                })

            if is_error:
                raise Exception(
                    "Table(s) validation failed : {}.".format(error_json))
            self.logger.info("Table schema successfully validated!")

        except Exception as ex:
            self.logger.exception(str(ex))
            super().save_exception_trace(str(ex))
            raise ex            
