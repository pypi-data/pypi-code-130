from marshmallow import (
    Schema,
    fields,
    validate,
)


class CompanyScientificLinkInterventionResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    company_scientific_link_id = fields.Integer(required=True)
    intervention_id = fields.Integer(required=True)
    score = fields.Float(required=True)
    preferred = fields.Boolean(allow_none=True)
    date = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime()
