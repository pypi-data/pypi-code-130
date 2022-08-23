from kk_ontology_module import map_data, load_onto, load_data, to_pandas

def test_to_pandas():
    onto = load_onto()
    data = load_data()
    map_data(onto, data)
    df = to_pandas(data, onto.Patient)
    assert df.iloc[0][1] == 10037882