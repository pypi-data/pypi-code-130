from marshmallow import (
    Schema,
    fields,
    validate,
)


class ArtifactQueueResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    source_type = fields.String(required=True)
    source_id = fields.Integer(required=True)
    artifact_mappings = fields.String(allow_none=True)
    date = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime()
