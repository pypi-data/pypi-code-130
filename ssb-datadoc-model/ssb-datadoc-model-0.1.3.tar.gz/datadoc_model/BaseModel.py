from pydantic import BaseModel


class DataDocBaseModel(BaseModel):
    """Defines configuration which applies to all Models in this application"""

    class Config:
        # Runs validation when a field value is assigned, not just in the constructor
        validate_assignment = True
        # Write only the values of enums during serialization
        use_enum_values = True
