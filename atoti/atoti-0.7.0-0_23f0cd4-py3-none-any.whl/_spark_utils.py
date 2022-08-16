from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Mapping

if TYPE_CHECKING:
    # Spark is only imported for type checking as we don't want it as a dependency
    from pyspark.sql import (  # pylint: disable=undeclared-dependency
        DataFrame,
        SparkSession,
    )

_SPARK_PROPERTIES = {"spark.sql.parquet.outputTimestampType": "TIMESTAMP_MICROS"}


def write_spark_to_parquet(
    dataframe: DataFrame,
    *,
    directory: Path,
) -> None:
    spark = dataframe.sql_ctx.sparkSession
    # Modify output format of timestamp columns
    # https://github.com/apache/spark/blob/7281784883d6bacf3d024397fd90edf65c06e02b/sql/catalyst/src/main/scala/org/apache/spark/sql/internal/SQLConf.scala#L399
    previous_props = _set_properties(spark, _SPARK_PROPERTIES)
    try:
        dataframe.write.parquet(_to_hadoop_file_path(directory))
    finally:
        _set_properties(spark, previous_props)


def _to_hadoop_file_path(path: Path) -> str:
    return path.as_uri()


def _set_properties(
    spark: SparkSession,
    props: Mapping[str, str],
) -> Dict[str, str]:
    """Set the given properties to the session and return the previous ones.

    Args:
        spark: The Spark session.
        props: The properties to set.

    Returns:
        The previous values of the changed properties.
    """
    previous = {}
    for prop, value in props.items():
        previous[prop] = spark.conf.get(prop, default=None)
        if value is None:
            spark.conf.unset(prop)
        else:
            spark.conf.set(prop, value)
    return previous
