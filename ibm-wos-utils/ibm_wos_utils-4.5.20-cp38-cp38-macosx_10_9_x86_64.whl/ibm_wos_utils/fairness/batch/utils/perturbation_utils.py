# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import random

try:
    from pyspark.sql import SparkSession, Window
    from pyspark.sql.dataframe import DataFrame
    from pyspark.sql.functions import array, explode, lit, monotonically_increasing_id, row_number, udf
    from pyspark.sql.types import ArrayType, FloatType, IntegerType, LongType, StringType
except ImportError as ie:
    pass

from ibm_wos_utils.fairness.batch.utils.date_util import DateUtil
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.fairness.batch.utils.sql_utils import SQLUtils


class PerturbationUtils():

    @classmethod
    def perform_perturbation(cls, data: DataFrame, column_to_perturb: str, from_group, to_groups: list, spark: SparkSession, numerical_perturb_count_per_row: int=None, float_decimal_place_precision: int=None, numerical_perturb_seed: int=0) -> DataFrame:
        """
        Performs perturbation on the given Spark data-frame (transformations) and returns the perturbed data frame.
        :data: The Spark data frame containing the data to be perturbed.
        :column_to_perturb: The column name on which perturbation is to be performed.
        :from_group: The group on which the perturbation is to be performed. [String in case of categorical columns and list (containing the range) in case of numerical columns.]
        :to_groups: The list of groups to which the perturbation is to be performed. [List of strings in case of categorical columns and list of lists (containing the ranges) in case of numerical columns.]
        :spark: The SparkSession object.
        :numerical_perturb_count_per_row: [Optional] The number of perturbed rows to be generated per row for numerical perturbation.
        :float_decimal_place_precision: [Optional] The decimal place precision to be used for numerical perturbation when data is float.
        :numerical_perturb_seed: [Optional] The seed to be used for numerical perturbation while picking up random values.
        
        :returns: A data-frame containing the perturbed records of all `to_groups`.
        """
        perturbed_df = None

        # Checking of the column is categorical or numerical
        is_categorical = isinstance(data.schema[column_to_perturb].dataType, StringType)

        if is_categorical:
            # Performing the categorical perturbation
            perturbed_df = cls._categorical_perturbation(data, column_to_perturb, from_group, to_groups, spark)
        else:
            # Performing the numerical perturbation
            perturbed_df = cls._numerical_perturbation(data, column_to_perturb, from_group, to_groups, numerical_perturb_count_per_row, float_decimal_place_precision, numerical_perturb_seed, spark)

        return perturbed_df
    
    @classmethod
    def _categorical_perturbation(cls, data: DataFrame, column_to_perturb: str, from_group: str, to_groups: list[str], spark: SparkSession) -> DataFrame:
        """
        Performs the categorical perturbation on the given Spark data-frame (transformations) and returns the perturbed data frame.
        :data: The Spark data frame containing the data to be perturbed.
        :column_to_perturb: The column name on which perturbation is to be performed.
        :from_group: The group name (string) on which the perturbation is to be performed.
        :to_groups: The list of group names (string) to which the perturbation is to be performed.
        :spark: The SparkSession object.
        
        :returns: A data-frame containing the perturbed records of all `to_groups`.
        """
        perturbed_df = None
        start_time = DateUtil.current_milli_time()

        # Initialising the perturbed data-frame
        perturbed_df = spark.createDataFrame([], data.schema)

        # Taking the rows that belong to the `from_group`
        from_group_query = SQLUtils.get_cat_filter_query(
            col_name=column_to_perturb,
            operator="==",
            values=[from_group]
        )
        print("Query filter used for the from group {} is: {}".format(from_group, from_group_query))
        from_group_df = data.where(from_group_query)

        # Performing perturbation (transformations) for each `to_group`
        perturbed_df = from_group_df.withColumn(column_to_perturb, explode(array([lit(to_group) for to_group in to_groups])))
        
        end_time = DateUtil.current_milli_time()
        print("Time taken for categorical perturbation of {} column was {} milliseconds.".format(column_to_perturb, end_time - start_time))

        return perturbed_df
    
    @classmethod
    def _numerical_perturbation(cls, data: DataFrame, column_to_perturb: str, from_group: list, to_groups: list[list], numerical_perturb_count_per_row: int, float_decimal_place_precision: int, numerical_perturb_seed: int, spark: SparkSession) -> DataFrame:
        """
        Performs the categorical perturbation on the given Spark data-frame (transformations) and returns the perturbed data frame.
        :data: The Spark data frame containing the data to be perturbed.
        :column_to_perturb: The column name on which perturbation is to be performed.
        :from_group: The group range on which the perturbation is to be performed.
        :to_groups: The list of group ranges to which the perturbation is to be performed.
        :numerical_perturb_count_per_row: The number of perturbed rows to be generated per row for numerical perturbation.
        :float_decimal_place_precision: The decimal place precision to be used for numerical perturbation when data is float.
        :numerical_perturb_seed: The seed to be used for numerical perturbation while picking up random values.
        :spark: The SparkSession object.
        
        :returns: A data-frame containing the perturbed records of all `to_groups`.
        """
        perturbed_df = None
        start_time = DateUtil.current_milli_time()

        # Checking if the column is integer type or not
        is_int = isinstance(data.schema[column_to_perturb].dataType, IntegerType) or isinstance(data.schema[column_to_perturb].dataType, LongType)

        # Taking the rows that belong to the `from_group`
        from_group_query = SQLUtils.get_num_filter_query(
            col_name=column_to_perturb,
            ranges=[from_group],
            include=True
        )
        print("Query filter used for the from group {} is: {}".format(from_group, from_group_query))
        from_group_df = data.where(from_group_query)
        from_group_count = from_group_df.count()

        # Calculating the total number of perturbations per row
        total_num_perturbations_per_row = len(to_groups) * numerical_perturb_count_per_row

        # Creating the duplicate rows to be perturbed
        n_to_array = udf(lambda n : [n] * total_num_perturbations_per_row, ArrayType(IntegerType() if is_int else FloatType()))
        perturbed_df = data.withColumn(column_to_perturb, n_to_array(data[column_to_perturb]))
        perturbed_df = perturbed_df.withColumn(column_to_perturb, explode(perturbed_df[column_to_perturb]))

        # Generating the perturbed values
        perturbed_values = []
        # Setting the random seed
        random.seed(numerical_perturb_seed)
        for _1 in range(from_group_count):
            # For each row in `from_group` generating the perturbed value using random values from `to_group`
            for to_group in to_groups:
                for _2 in range(numerical_perturb_count_per_row):
                    if is_int:
                        perturbed_value = random.randint(to_group[0], to_group[1])
                    else:
                        perturbed_value = random.uniform(to_group[0], to_group[1])
                        if float_decimal_place_precision is not None:
                            perturbed_value = perturbed_value.__round__(float_decimal_place_precision)
                    
                    perturbed_values.append(perturbed_value)
        
        # Adding the perturbed values generated to the perturbed data frame
        # Convert list to a dataframe
        pert_col_name = "{}_pert".format(column_to_perturb)
        pert_val_df = spark.createDataFrame([(l,) for l in perturbed_values], [pert_col_name])

        # Add 'sequential' index and join both dataframe to get the final result
        perturbed_df = perturbed_df.withColumn("row_idx", row_number().over(Window.partitionBy(lit(0)).orderBy(monotonically_increasing_id())))
        pert_val_df = pert_val_df.withColumn("row_idx", row_number().over(Window.partitionBy(lit(0)).orderBy(monotonically_increasing_id())))

        # Joining the perturbed value data from with perturbed data frame and replacing the column to be perturbed
        perturbed_df = perturbed_df.join(pert_val_df, perturbed_df["row_idx"] == pert_val_df["row_idx"]).drop("row_idx").drop(column_to_perturb).withColumnRenamed(pert_col_name, column_to_perturb)

        end_time = DateUtil.current_milli_time()
        print("Time taken for numerical perturbation of {} column was {} milliseconds.".format(column_to_perturb, end_time - start_time))

        return perturbed_df