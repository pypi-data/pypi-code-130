import uuid

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from syndb_cassandra.utils.misc import get_class_names


class Mesh(Model):
    __table_name__ = "mesh"

    cid = columns.UUID(primary_key=True, default=uuid.uuid4())

    centroid_xyz = columns.Tuple(columns.Float(), columns.Float(), columns.Float())
    euclidean_rotation_xyz = columns.Tuple(columns.Float(), columns.Float(), columns.Float())

    object_id = columns.UUID(required=True)

    mesh_path = columns.Text(required=True)


class MeshSegment(Model):
    __table_name__ = "mesh_segment"

    object_id = columns.UUID(primary_key=True)
    model_name = columns.Ascii(primary_key=True, required=True, clustering_order="DESC", max_length=35)

    mesh_id = columns.UUID(required=True)
    vertex_indices = columns.List(value_type=columns.Integer, required=True)


mesh_models = (Mesh, MeshSegment)
mesh_model_names = get_class_names(mesh_models)
