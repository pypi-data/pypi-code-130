from logging import warning
from typing import Iterable, Optional, Union

from cassandra.cluster import Session
from cassandra.cqlengine.models import Model
from syndb_cassandra.utils.misc import (
    materialized_view_name_from_table_name_and_partition_key,
)


def join_null_check_columns(column_keys):
    return " ".join(f"AND {key} IS NOT NULL" for key in column_keys)


def create_materialized_view(
    cassandra_session: Session,
    keyspace_name: str,
    cassandra_model: Model,
    new_partition_key: str | Iterable[str],
    name_of_materialized_view: Optional[str] = None,
    old_partition_keys_as_last_clustering_keys: bool = True,
    user_defined_clustering_keys: Optional[list[str]] = None,
):
    number_of_additional_primary_keys = 0
    if isinstance(new_partition_key, str):
        if new_partition_key not in cassandra_model._primary_keys.keys():
            number_of_additional_primary_keys += 1

        new_partition_key_string = new_partition_key
        clustering_keys = [ck for ck in cassandra_model._primary_keys.keys() if ck != new_partition_key]

        partition_key_null_check_row = f"WHERE {new_partition_key} IS NOT NULL"
    else:
        new_partition_key = tuple(new_partition_key)
        for single_new_partition_key in new_partition_key:
            if single_new_partition_key not in cassandra_model._primary_keys.keys():
                number_of_additional_primary_keys += 1

        new_partition_key_string = f"({', '.join(new_partition_key)})"
        clustering_keys = [ck for ck in cassandra_model._primary_keys.keys() if ck not in new_partition_key]

        partition_key_null_check_row = (
            f"WHERE {new_partition_key[0]} IS NOT NULL {join_null_check_columns(new_partition_key[1:])}"
        )

    name_of_new_view = name_of_materialized_view or materialized_view_name_from_table_name_and_partition_key(
        cassandra_model.__table_name__, new_partition_key
    )

    if user_defined_clustering_keys:
        for ck in clustering_keys:
            if ck not in user_defined_clustering_keys:
                user_defined_clustering_keys.append(ck)
        clustering_keys = user_defined_clustering_keys
    elif old_partition_keys_as_last_clustering_keys:
        for old_partition_key in cassandra_model._partition_keys.keys():
            if old_partition_key in clustering_keys:
                clustering_keys.remove(old_partition_key)
                clustering_keys.append(old_partition_key)

    for ck in clustering_keys:
        if ck not in cassandra_model._primary_keys.keys():
            number_of_additional_primary_keys += 1

    if number_of_additional_primary_keys > 1:
        warning(
            f"number_of_additional_primary_keys is higher than 1 ({number_of_additional_primary_keys}). "
            f"The generation of the materialized view should fail"
        )

    cassandra_session.execute(
        (
            f"CREATE MATERIALIZED VIEW {keyspace_name}.{name_of_new_view} AS"
            f"  SELECT * FROM {keyspace_name}.{cassandra_model.__table_name__}"
            f"  {partition_key_null_check_row} {join_null_check_columns(clustering_keys)}"
            f"  PRIMARY KEY ({new_partition_key_string}, {', '.join(clustering_keys)})"
            f"  WITH comment='Allow query by {new_partition_key_string} instead of ({''.join(cassandra_model._partition_keys.keys())})';"
        )
    )

    return name_of_new_view
