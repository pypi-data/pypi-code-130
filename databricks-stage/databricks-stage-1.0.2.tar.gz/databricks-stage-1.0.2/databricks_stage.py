import argparse
from pyspark.sql import SparkSession

# Used for high-speed ingest from Databricks. Is meant to be run as part of a Databricks job.
def run(access_key_id, secret_access_key, sql_query, stage_output_bucket, stage_output_prefix):
    spark = SparkSession.builder.getOrCreate()

    df = spark.sql(f"""{sql_query}""")
    df.write \
        .format("csv") \
        .option("compression", "gzip") \
        .option("nullValue", "_SISU_NULL") \
        .option("delimiter", "\x1e") \
        .mode("overwrite") \
        .save(f"s3a://{access_key_id}:{secret_access_key}@{stage_output_bucket}/{stage_output_prefix}")

