from kk_ontology_module import map_data, load_onto, load_data, to_pandas, CancerOntology, test_data

def test_reason():
    o = CancerOntology()
    o.define_data(test_data)
    o.reason()
    df = to_pandas(test_data, o.onto.TaxaneContainingRegimen)

    assert df.iloc[0][1] == 10037882