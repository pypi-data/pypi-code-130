from typing import Optional
from uuid import UUID

from pydantic import validate_arguments
from syndb_cassandra.models import SYNDB_OWNER_KEYSPACE, Owner
from syndb_cassandra.settings import SyndbCassandraSettings, cassandra_settings_getter

SYNDB_OWNER_TABLE = f"{SYNDB_OWNER_KEYSPACE}.{Owner.__table_name__}"


def _get_connection(settings: Optional[SyndbCassandraSettings] = None):
    settings = settings or cassandra_settings_getter()()
    return settings.cassandra_connection()


@validate_arguments
def add_owner(
    owner_id: UUID, settings: Optional[SyndbCassandraSettings] = None
) -> None:
    assert _get_connection(settings).execute(
        f"INSERT INTO {SYNDB_OWNER_TABLE} (cid) VALUES ({owner_id}) IF NOT EXISTS"
    )


@validate_arguments
def add_dataset(
    owner_id: UUID,
    animal_name: str,
    doi: Optional[str] = None,
    brain_structure: Optional[str] = None,
    microscopy: Optional[str] = None,
    mutation_tags: Optional[tuple[str]] = None,
    label: Optional[str] = None,
    settings: Optional[SyndbCassandraSettings] = None,
) -> None:
    _get_connection(settings).execute(
        f"INSERT INTO {SYNDB_OWNER_TABLE} "
        f"(owner_id, animal_name, doi, brain_structure, microscopy, mutation_tags, label) "
        f"VALUES ({owner_id}, {animal_name}, {doi}, {brain_structure}, {microscopy}, {mutation_tags}, {label}) "
        f"IF NOT EXISTS"
    )
