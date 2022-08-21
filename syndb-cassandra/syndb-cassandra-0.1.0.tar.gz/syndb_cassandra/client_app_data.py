import json
import pkgutil
from collections import defaultdict
from pathlib import Path
from typing import Optional

from cassandra.cqlengine import columns
from orjson import orjson
from syndb_cassandra.models import (
    all_models,
    brain_unit_model_names,
    structure_model_names,
)
from syndb_cassandra.models.dendrite_axon import dendrite_axon_model_names
from syndb_cassandra.models.mesh import Mesh, mesh_model_names
from syndb_cassandra.models.metadata import Dataset, parent_model_names
from syndb_cassandra.models.organelle import organelle_model_names
from syndb_cassandra.utils.column_types_to_python import (
    COLLECTION_COLUMN_TYPES_TO_DART,
    COLUMN_TYPES_TO_DART,
)
from syndb_cassandra.utils.misc import (
    materialized_view_name_from_table_name_and_partition_key,
)


def client_app_data(out_file_path: Optional[Path] = None, dry_run: bool = False) -> dict:
    """
    The following generates a JSON with the metadata for the highly dynamic forms in the SynDB client application.
    """
    (
        table_schemas,
        column_types,
        collection_column_typings,
        table_metadata,
        semi_generic_columns,
        required,
        table_name_to_column_names,
    ) = ({}, {}, {}, {}, {}, {}, {})

    # ======================================================================================================================
    global_columns = orjson.loads(pkgutil.get_data(__name__, "assets/global_columns.json"))

    columns_defined_from_dataset = []
    for column in Dataset._columns:
        if column == "cid":
            continue
        columns_defined_from_dataset.append(column)

    for model in all_models:
        model_name = model.__table_name__
        for partition_key, partition_type in model._partition_keys.items():
            # Initialise all partition key sets (partition key, and composite keys) for all tables
            table_metadata[model_name] = [(partition_key,)]

        table_schemas[model_name] = {}

        # Define fields that are generic for global definition during upload with the client application
        required_columns, column_names, data_str, data_bool = [], [], [], []
        for name, column in model._columns.items():
            column_names.append(name)
            table_schemas[model_name][name] = column.db_type
            if name not in column_types:
                column_types[name] = COLUMN_TYPES_TO_DART[column.db_type]
            if column.db_type in COLLECTION_COLUMN_TYPES_TO_DART:
                collection_column_typings[name] = COLLECTION_COLUMN_TYPES_TO_DART[column.db_type]

            if (column.required or column.is_primary_key) and (
                model_name == "dataset"  # Do not use the logic on the next line if dataset model
                or (name != "dataset_id" and name not in columns_defined_from_dataset)
            ):
                required_columns.append(name)

            if not (
                name in global_columns["all"] or model_name in global_columns and name in global_columns[model_name]
            ):
                # Only include columns that are defined in assets/global_columns.json
                continue

            if isinstance(column, columns.Ascii):
                data_str.append(name)
            if isinstance(column, columns.Boolean):
                data_bool.append(name)

        table_name_to_column_names[model_name] = column_names
        required[model_name] = required_columns

        if data_str or data_bool:
            semi_generic_columns[model_name] = {"bool": data_bool, "string": data_str}

    # ==================================================================================================================
    # Generate materialized view partition keys for every table

    for model_name in brain_unit_model_names:
        # All daughter models should have a materialized view with brain ID as partition key
        table_metadata[model_name].append(("brain_id",))

    # User-defined json can be accessed to define materialized views that have composite keys with brain_structure as
    # the first primary key:
    brain_structure_materialized_views_metadata = orjson.loads(
        pkgutil.get_data(__name__, "assets/brain_structure_materialized_views.json")
    )

    for (
        model,
        partition_key_2nd_in_pair_set,
    ) in brain_structure_materialized_views_metadata.items():
        for partition_key_2nd_in_pair in partition_key_2nd_in_pair_set:
            table_metadata[model].append(("brain_structure", partition_key_2nd_in_pair))

    # ==================================================================================================================
    # Materialized view metadata

    model_name_to_partition_keys_to_mv_name = defaultdict(dict)
    for (
        model_name,
        second_partition_fields,
    ) in brain_structure_materialized_views_metadata.items():
        for second_partition_field in second_partition_fields:
            composite_key = ("brain_structure", second_partition_field)
            model_name_to_partition_keys_to_mv_name[model_name][
                ",".join(composite_key)
            ] = materialized_view_name_from_table_name_and_partition_key(model_name, composite_key)

    model_name_to_partition_keys_to_mv_name["Mesh"] = {
        "object_id": materialized_view_name_from_table_name_and_partition_key(Mesh.__table_name__, "object_id")
    }

    # ==================================================================================================================
    # Store hierarchical data for each model

    model_name_to_parent_models = {}
    generic_daughter_hierarchy = ("brain", "neuron")
    for organelle in organelle_model_names:
        model_name_to_parent_models[organelle] = (
            *generic_daughter_hierarchy,
            *dendrite_axon_model_names,
        )

    for model_name in dendrite_axon_model_names:
        model_name_to_parent_models[model_name] = generic_daughter_hierarchy

    # ==================================================================================================================
    # Merge and export unified dataset for use in client application

    brain_tree = orjson.loads(pkgutil.get_data(__name__, "assets/neurometa/human_brain_tree.json"))
    model_organisms = orjson.loads(pkgutil.get_data(__name__, "assets/neurometa/model_organism.json"))
    neurotransmitters = orjson.loads(pkgutil.get_data(__name__, "assets/neurometa/neurotransmitters.json"))

    neuron_types = orjson.loads(pkgutil.get_data(__name__, "assets/neuron_types.json"))

    result = {
        "tablePartitionKeySets": table_metadata,
        "tableNameToPartitionKeysToMVName": model_name_to_partition_keys_to_mv_name,
        "tableNameToGenericColumns": semi_generic_columns,
        "tableHierarchy": model_name_to_parent_models,
        "tableNameToRequired": required,
        "tableNameToColumnNames": table_name_to_column_names,
        "genericColumnToChoices": {
            **neuron_types,
            "first_parent_model_name": structure_model_names,
            "brain_structure": brain_tree["neuronal_structure_flat"],
            "brain_structure_lower": [s.lower() for s in brain_tree["neuronal_structure_flat"]],
        },
        "valueTextMappedGenericColumnToChoices": {
            "neurotransmitter": neurotransmitters,
            "model_organism": model_organisms["Animals"],
        },
        "tableGroupsToMembers": {
            "parent_models": parent_model_names,
            "brain_unit_models": brain_unit_model_names,
            "mesh_models": mesh_model_names,
        },
        "brainStructureStandardNameToNames": brain_tree["standard_name_to_names"],
        "tableSchemas": table_schemas,
        "columnTypes": dict(sorted(column_types.items())),
        "collectionColumnTypings": dict(sorted(collection_column_typings.items())),
    }

    if out_file_path:
        with open(out_file_path / "client_app_data.json", "w") as out_json:
            json.dump(
                result,
                out_json,
            )
    elif dry_run:
        print(json.dumps(result, indent=2))

    return result
