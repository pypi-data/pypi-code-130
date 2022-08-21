import pkgutil
import uuid

from cassandra.cqlengine import ValidationError, columns
from cassandra.cqlengine.models import Model
from orjson import orjson

neuron_data = orjson.loads(pkgutil.get_data("syndb_cassandra", "assets/neuron_types.json"))


class Neuron(Model):
    __table_name__ = "neuron"

    brain_structure = columns.Ascii(primary_key=True, max_length=65)

    # Placement for model-specific clustering keys

    dataset_id = columns.UUID(primary_key=True)
    cid = columns.UUID(primary_key=True, default=uuid.uuid4())

    mutation_tags = columns.List(columns.Ascii(max_length=255))

    polarity = columns.Ascii(max_length=35)
    neuron_type = columns.Ascii(max_length=35)
    direction = columns.Ascii(max_length=35)

    volume = columns.Float()
    radius = columns.Float()
    surface_area = columns.Float()
    area_volume_ratio = columns.Float()
    sphericity = columns.Float()
    centroid_xyz = columns.Tuple(columns.Float(), columns.Float(), columns.Float())

    neuron_id = columns.UUID()

    is_mesh_segment = columns.Boolean(default=False)

    def validate(self):
        super().validate()
        if self.polarity and self.polarity not in neuron_data["polarity"]:
            msg = f"{self.polarity} is not a valid polarity, make sure that the characters are lowercase"
            raise ValidationError(msg)
        if self.neuron_type and self.neuron_type not in neuron_data["type"]:
            msg = f"{self.neuron_type} is not a valid neuron type, make sure that the characters are lowercase"
            raise ValidationError(msg)
        if self.direction and self.direction not in neuron_data["direction"]:
            msg = f"{self.direction} is not a valid direction, make sure that the characters are lowercase"
            raise ValidationError(msg)
