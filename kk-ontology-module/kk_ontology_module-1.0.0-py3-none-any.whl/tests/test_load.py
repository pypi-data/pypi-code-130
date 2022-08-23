from kk_ontology_module import load_data

def test_load():
    # df = load_data('src/kk_ontology_module/extras/m2dummyB_small.csv')
    df = load_data()
    assert df.iloc[0][1] == 10037882