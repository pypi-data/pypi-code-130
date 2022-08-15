import argparse
from pyspark.sql import SparkSession

# Used for high-speed ingest from Databricks. Is meant to be run as part of a Databricks job.
def databricks_stage():
    parser = argparse.ArgumentParser(description='Stage data for fast ingest.')
    parser.add_argument('access_key_id')
    parser.add_argument('secret_access_key')
    parser.add_argument('sql_query')
    parser.add_argument('stage_output_bucket')
    parser.add_argument('stage_output_prefix')

    args = parser.parse_args()

    spark = SparkSession.builder.getOrCreate()

    df = spark.sql(f"""{args.sql_query}""")
    df.write \
        .format("csv") \
        .option("compression", "gzip") \
        .option("nullValue", "_SISU_NULL") \
        .option("delimiter", "\x1e") \
        .mode("overwrite") \
        .save(f"s3a://{args.access_key_id}:{args.secret_access_key}@{args.stage_output_bucket}/{args.stage_output_prefix}")

