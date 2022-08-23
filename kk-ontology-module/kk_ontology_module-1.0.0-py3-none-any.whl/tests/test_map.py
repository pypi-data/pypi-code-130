from kk_ontology_module import map_data, load_onto, load_data

def test_map():
    onto = load_onto()
    data = load_data()
    map_data(onto, data)
    assert onto.patient1.PatientID[0] == 810037882