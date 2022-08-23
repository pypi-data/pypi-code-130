import pandas as pd
import numpy as np
from kk_ontology_module.load_onto import load_onto

def to_pandas(df, onto_class, IDcolname="LINKNUMBER", returns='patient', onto=load_onto()):
    """
    Arguments: 
    df = full dataframe (containing all data)
    onto_class = can be regimen or tumour subclass that you would like to return individuals of
    IDcolname = column name of the PatientID (NHS number, Link number, etc.), TumourID or RegimenID
    onto = full ontology

    Takes all instances of the ontology regimen class and returns the pandas df.
    Currently only supports regimen, tumour and patient subclasses.
    """
    patientIDs = []
    tumourIDs = []
    regimenIDs = []
    
    for instance in onto_class.instances():
        ### TODO: Add functionality for DRUG instances

        if (onto.search(subclass_of = onto.Regimen).count(onto_class)):
        # if onto_class in onto.Regimen.subclasses():
            try:
                patientIDs.append(instance.treats[0].belongs_to_patient[0].PatientID[0])
                tumourIDs.append(instance.treats[0].TumourID[0])
                regimenIDs.append(instance.RegimenID[0])
            except:
                print("Empty instance")
        elif (onto.search(subclass_of = onto.Tumour).count(onto_class)):
        # elif onto_class in onto.Tumour.subclasses():
            try:
                patientIDs.append(instance.belongs_to_patient[0].PatientID[0])
                tumourIDs.append(instance.TumourID[0])
                regimenIDs.append(instance.treated_by[0].RegimenID[0])
            except:
                print("Empty instance")
        elif (onto.search(subclass_of = onto.Patient).count(onto_class)):
        # elif onto_class in onto.Patient.subclasses():
            try:
                patientIDs.append(instance.PatientID[0])
                tumourIDs.append(instance.has_tumour[0].TumourID)
                regimenIDs.append(instance.has_tumour[0].treated_by[0].RegimenID[0])
            except:
                print("Empty instance")
        else:
            print("Class is not supported. Currently supported subclasses are of type Regimen, Tumour, and Patient.")
            return

    # print(patientIDs)
    # returns the dataframe where patientID is included
    if returns=='patient':
        return df[df[IDcolname].isin(patientIDs)]
    elif returns=='regimen':
        return df[df[IDcolname].isin(regimenIDs)]
    elif returns=='tumour':
        return df[df[IDcolname].isin(tumourIDs)]
    else:
        print("Error: returns must be set to patient, regimen or tumour (as a string)")
        return

default_breast_cancer_codes = ['C50', 'C500','C501','C502','C503','C504','C505','C506','C507','C508','C509']
def has_icd10_code(df, icd10colname='PRIMARY_DIAGNOSIS', codes=default_breast_cancer_codes):
    """
    df = pandas dataframe with data
    icd10colname = column name of the ICD10 codes
    codes = python list of codes that you would like to filter by
    """
    return df[df[icd10colname].isin(codes)]

def has_morphology_code(df, morphcolname='MORPH_ICD10_O2', codes=[8090]):
    """
    df = pandas dataframe with data
    morphcolname = column name of the morphology code
    codes = python list of codes that you would like to filter by
    """
    return df[df[morphcolname].isin(codes)]


# TODO: Add numpy support