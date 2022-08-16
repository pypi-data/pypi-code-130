import argparse
from pyspark.sql import SparkSession

# Used for high-speed ingest from Databricks. Is meant to be run as part of a Databricks job.
def run(**kwargs):
    spark = SparkSession.builder.getOrCreate()

    print("KWARGS", kwargs)

    df = spark.sql(f"""{kwargs['sql_query']}""")
    df.write \
        .format("csv") \
        .option("compression", "gzip") \
        .option("nullValue", "_SISU_NULL") \
        .option("delimiter", "\x1e") \
        .mode("overwrite") \
        .save(f"s3a://{kwargs['access_key_id']}:{kwargs['secret_access_key']}@{kwargs['stage_output_bucket']}/{kwargs['stage_output_prefix']}")

