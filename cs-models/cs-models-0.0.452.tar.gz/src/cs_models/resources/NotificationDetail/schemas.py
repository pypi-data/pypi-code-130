from marshmallow import (
    Schema,
    fields,
    validate,
)


class NotificationDetailResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    notification_id = fields.Integer(required=True)
    company_matches = fields.String(required=True)
    drug_matches = fields.String(required=True)
    disease_matches = fields.String(required=True)
    target_matches = fields.String(required=True)
    updated_at = fields.DateTime()
