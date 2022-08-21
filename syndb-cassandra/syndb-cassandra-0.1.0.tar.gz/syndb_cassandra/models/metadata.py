import uuid
from datetime import datetime

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from syndb_cassandra.utils.misc import get_class_names


class Owner(Model):
    __table_name__ = "owner"

    cid = columns.UUID(primary_key=True)
    dataset_ids = columns.List(columns.UUID())


class Dataset(Model):
    __table_name__ = "dataset"

    owner_id = columns.UUID(primary_key=True)

    animal_name = columns.Ascii(primary_key=True, max_length=255, clustering_order="DESC")
    created_on = columns.DateTime(primary_key=True, default=datetime.utcnow())

    cid = columns.UUID(primary_key=True, default=uuid.uuid4())

    upload_complete = columns.Boolean(default=False)
    doi = columns.Ascii(max_length=100)

    brain_structure = columns.Ascii(default="plural", max_length=65)

    microscopy = columns.Ascii(max_length=100)
    mutation_tags = columns.List(columns.Ascii(max_length=255))

    label = columns.Ascii(max_length=100)


parent_models = (Owner, Dataset)
parent_model_names = get_class_names(parent_models)
