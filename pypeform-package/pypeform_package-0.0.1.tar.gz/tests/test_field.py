from pypeform import Field


def test_field_from_definition_json():
    import json

    with open('data/body_formatted.json') as f:
        event_data = json.load(f)

    fields = event_data['form_response']['definition']['fields']

    for field in fields:
        field = Field.from_definition_json(field)
        assert isinstance(field, Field)
