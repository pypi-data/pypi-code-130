from marshmallow import (
    Schema,
    fields,
    validate,
)


class NotificationResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    search_id = fields.Integer(required=True)
    source_type = fields.String(required=True)
    source_id = fields.Integer(required=True)
    matches = fields.String(allow_none=True)
    seen = fields.Boolean(allow_none=True)
    date = fields.DateTime(required=True)
    updated_at = fields.DateTime()
