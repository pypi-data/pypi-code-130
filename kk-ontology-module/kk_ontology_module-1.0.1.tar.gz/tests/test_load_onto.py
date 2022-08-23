from kk_ontology_module import load_onto

def test_load_onto():
    onto = load_onto()
    assert onto.Thing == onto.Thing