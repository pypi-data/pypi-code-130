import pkgutil
from functools import partial
from typing import Optional

import orjson
from cassandra.cqlengine.management import (
    create_keyspace_simple,
    drop_keyspace,
    sync_table,
)
from syndb_cassandra.models import (
    NEURO_DATA_MODIFY_ROLE_NAME,
    NEURO_DATA_READ_ROLE_NAME,
    SYNDB_NEURO_DATA_KEYSPACE,
    keyspace_to_models,
    model_name_to_model,
)
from syndb_cassandra.models.mesh import Mesh
from syndb_cassandra.settings import SyndbCassandraSettings, cassandra_settings_getter
from syndb_cassandra.utils.create_materialized_view import create_materialized_view


def create_syndb_tables(settings: Optional[SyndbCassandraSettings] = None) -> None:
    settings = settings or cassandra_settings_getter()()
    current_connection = settings.cassandra_connection()

    if settings.remove_pre_existing_syndb:
        drop_keyspace(
            SYNDB_NEURO_DATA_KEYSPACE,
            connections=[settings.cassandra_connection_name],
        )

    # create_syndb_tables ==============================================================================================

    for keyspace, models in keyspace_to_models.items():
        create_keyspace_simple(
            keyspace,
            replication_factor=1,
            connections=[settings.cassandra_connection_name],
        )

        for model in models:
            sync_table(
                model,
                keyspaces=(keyspace,),
                connections=(settings.cassandra_connection_name,),
            )

    partial_mv = partial(
        create_materialized_view, current_connection, SYNDB_NEURO_DATA_KEYSPACE
    )
    brain_structure_materialized_views_metadata = orjson.loads(
        pkgutil.get_data(
            "syndb_cassandra", "assets/brain_structure_materialized_views.json"
        )
    )

    for (
        model_name,
        second_partition_fields,
    ) in brain_structure_materialized_views_metadata.items():
        for second_partition_field in second_partition_fields:
            partial_mv(
                model_name_to_model[model_name],
                ("brain_structure", second_partition_field),
            )
    partial_mv(Mesh, "object_id")


def create_roles(settings: Optional[SyndbCassandraSettings] = None) -> None:
    settings = settings or cassandra_settings_getter()()
    current_connection = settings.cassandra_connection()

    current_connection.execute(
        f"CREATE ROLE IF NOT EXISTS {NEURO_DATA_MODIFY_ROLE_NAME}"
    )
    current_connection.execute(
        f"GRANT ALTER on KEYSPACE {SYNDB_NEURO_DATA_KEYSPACE} to {NEURO_DATA_MODIFY_ROLE_NAME}"
    )
    current_connection.execute(
        f"GRANT SELECT on KEYSPACE {SYNDB_NEURO_DATA_KEYSPACE} to {NEURO_DATA_MODIFY_ROLE_NAME}"
    )

    current_connection.execute(f"CREATE ROLE IF NOT EXISTS {NEURO_DATA_READ_ROLE_NAME}")
    current_connection.execute(
        f"GRANT SELECT on KEYSPACE {SYNDB_NEURO_DATA_KEYSPACE} to {NEURO_DATA_READ_ROLE_NAME}"
    )
