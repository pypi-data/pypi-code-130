from pypeform import Event, FormResponse


def test_event_from_json():
    import json
    with open('data/body_formatted.json') as f:
        body_data = json.load(f)

    event = Event.from_event_json(event_json=body_data)
    assert isinstance(event, Event)

    # check basic values
    assert event.event_id == '01GAZ4HA6EK6DP36SG6P3Y4ANM'
    assert event.event_type == 'form_response'

    # check types are correct
    assert isinstance(event.form_response, FormResponse)
