from pypeform import FormResponse, Variable, Answer, Field


def test_formresponse_from_json():
    import json
    from datetime import datetime
    import pytz

    with open('data/body_formatted.json') as f:
        body_data = json.load(f)

    form_response_json = body_data['form_response']

    fr = FormResponse.from_form_response_json(form_response_json=form_response_json)

    assert isinstance(fr, FormResponse)

    # check basic values
    assert fr.form_id == 'sRmK2H1s'
    assert fr.token == '7ax1kv4zahmlj1d9m7ax150zqknp9jci'
    assert fr.landed_at == datetime(2022, 8, 21, 2, 41, 32, tzinfo=pytz.UTC)
    assert fr.submitted_at == datetime(2022, 8, 21, 2, 43, 28, tzinfo=pytz.UTC)

    # check Variable types
    assert isinstance(fr.variables, dict) or fr.variables is None
    if fr.variables is not None:
        assert all(isinstance(key, str) for key in fr.variables.keys())
        assert all(isinstance(value, Variable) for value in fr.variables.values())

    # check Answer types
    assert isinstance(fr.answers, dict)
    assert all(isinstance(key, str) for key in fr.answers.keys())
    assert all(isinstance(value, Answer) for value in fr.answers.values())

    # check Field types
    assert isinstance(fr.fields, dict)
    assert all(isinstance(key, str) for key in fr.fields.keys())
    assert all(isinstance(value, Field) for value in fr.fields.values())
