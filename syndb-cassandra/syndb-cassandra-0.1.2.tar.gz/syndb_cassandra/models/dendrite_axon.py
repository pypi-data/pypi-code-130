import uuid

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from syndb_cassandra.utils.misc import get_class_names


class Dendrite(Model):
    __table_name__ = "dendrite"

    brain_structure = columns.Ascii(primary_key=True, max_length=65)

    # Placement for model-specific clustering keys

    dataset_id = columns.UUID(primary_key=True)
    cid = columns.UUID(primary_key=True, default=uuid.uuid4())

    mutation_tags = columns.List(columns.Ascii(max_length=255))

    post_synaptic_terminal_count = columns.Integer()

    volume = columns.Float()

    radius = columns.Float()
    surface_area = columns.Float()
    area_volume_ratio = columns.Float()
    sphericity = columns.Float()
    centroid_xyz = columns.Tuple(columns.Float(), columns.Float(), columns.Float())

    first_parent_id = columns.UUID()
    first_parent_model_name = columns.Ascii()

    neuron_id = columns.UUID()

    is_mesh_segment = columns.Boolean(default=False)


class Axon(Model):
    __table_name__ = "axon"

    brain_structure = columns.Ascii(primary_key=True, max_length=65)

    # Placement for model-specific clustering keys

    dataset_id = columns.UUID(primary_key=True)
    cid = columns.UUID(primary_key=True, default=uuid.uuid4())

    mutation_tags = columns.List(columns.Ascii(max_length=255))

    pre_synaptic_terminal_count = columns.Integer()

    volume = columns.Float()

    radius = columns.Float()
    surface_area = columns.Float()
    area_volume_ratio = columns.Float()
    sphericity = columns.Float()
    centroid_xyz = columns.Tuple(columns.Float(), columns.Float(), columns.Float())

    first_parent_id = columns.UUID()
    first_parent_model_name = columns.Ascii()

    neuron_id = columns.UUID()

    is_mesh_segment = columns.Boolean(default=False)


class Terminal(Model):
    __table_name__ = "terminal"

    brain_structure = columns.Ascii(primary_key=True, max_length=65)

    # Placement for model-specific clustering keys
    is_pre_synaptic = columns.Boolean(primary_key=True)

    dataset_id = columns.UUID(primary_key=True)
    cid = columns.UUID(primary_key=True, default=uuid.uuid4())

    mutation_tags = columns.List(columns.Ascii(max_length=255))

    volume = columns.Float()

    mitochondria_count = columns.Integer()
    total_mitochondria_volume = columns.Float()

    vesicle_count = columns.Integer()
    total_vesicle_volume = columns.Float()

    radius = columns.Float()
    surface_area = columns.Float()
    area_volume_ratio = columns.Float()
    sphericity = columns.Float()
    centroid_xyz = columns.Tuple(columns.Float(), columns.Float(), columns.Float())

    first_parent_id = columns.UUID()
    first_parent_model_name = columns.Ascii()

    neuron_id = columns.UUID()

    is_mesh_segment = columns.Boolean(default=False)


dendrite_axon_models = (
    Dendrite,
    Axon,
    Terminal,
)
dendrite_axon_model_names = get_class_names(dendrite_axon_models)
