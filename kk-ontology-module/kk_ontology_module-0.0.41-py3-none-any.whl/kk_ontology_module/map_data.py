from owlready2 import *
import pandas as pd

class Instances():
    patients = []
    tumours = []
    drugs = []
    regimens = []

i = Instances()

def map_data(onto, data_to_map):
    ## --------------------- HELPER FUNCTIONS ---------------------
    def fec(instances, regimen):
        '''
        For handling the case where "FEC" is included in the regimen
        '''
        instances.drugs.append(onto.Drug(has_drug_reference=[onto.Fluorouracil5REF], part_of_regimen=[regimen]))
        instances.drugs.append(onto.Drug(has_drug_reference=[onto.EpirubicinREF], part_of_regimen=[regimen]))
        instances.drugs.append(onto.Drug(has_drug_reference=[onto.CyclophosphamideREF], part_of_regimen=[regimen]))

    def create_drug_instances(string, regimen):
        '''
        Creating drug instances beased on the string (string describes the drugs)
        TODO: add more drug compatibility.
        '''
        if "capecitabine" in string.lower():
            i.drugs.append(onto.Drug(has_drug_reference=[onto.CapecitabineREF], part_of_regimen=[regimen]))
        if "carboplatin" in string.lower():
            i.drugs.append(onto.Drug(has_drug_reference=[onto.CarboplatinREF], part_of_regimen=[regimen]))
        if "cyclophosphamide" in string.lower():
            i.drugs.append(onto.Drug(has_drug_reference=[onto.CyclophosphamideREF], part_of_regimen=[regimen]))
        if "docetaxel" in string.lower():
            i.drugs.append(onto.Drug(has_drug_reference=[onto.DocetaxelREF], part_of_regimen=[regimen]))
        if "epirubicin" in string.lower():
            i.drugs.append(onto.Drug(has_drug_reference=[onto.EpirubicinREF], part_of_regimen=[regimen]))
        if "fluorouracil" in string.lower():
            i.drugs.append(onto.Drug(has_drug_reference=[onto.Fluorouracil5REF], part_of_regimen=[regimen]))
        if "paclitaxel" in string.lower():
            i.drugs.append(onto.Drug(has_drug_reference=[onto.PaclitaxelREF], part_of_regimen=[regimen]))
        if "pertuzumab" in string.lower():
            i.drugs.append(onto.Drug(has_drug_reference=[onto.PertuzumabREF], part_of_regimen=[regimen]))
        if "trastuzumab" in string.lower():
            i.drugs.append(onto.Drug(has_drug_reference=[onto.TrastuzumabREF], part_of_regimen=[regimen]))
        if "FEC" in string:
            fec(i, regimen)
    
    def onto_behaviour_code(onto, code):
        '''
        Converts an integer (behaviour code) into the BehaviourCodeREF instance in ontology
        '''
        if code == 0:
            return onto.BehaviourCode0REF
        if code == 1:
            return onto.BehaviourCode1REF
        if code == 2:
            return onto.BehaviourCode2REF
        if code == 3:
            return onto.BehaviourCode3REF
        if code == 5:
            return onto.BehaviourCode5REF
        if code == 6:
            return onto.BehaviourCode6REF
        if code == 9:
            return onto.BehaviourCode9REF
        return 0 # error case
    
    def tumour_icd10_code(onto, code):
        '''
        Converts string of ICD10 code to Tumour ICD10 code REF instance in ontology.
        '''
        code1 = code[0] ## First letter
        code2 = code[1:3] ## First 2 numbers
        if code1 == "C":
            if 0 <= int(code2) <= 14:
                return onto.C00_C14_REF
            if 15 <= int(code2) <= 26:
                return onto.C15_C26_REF
            if 30 <= int(code2) <= 39:
                return onto.C30_C39_REF
            if 40 <= int(code2) <= 41:
                return onto.C40_C41_REF
            if 43 <= int(code2) <= 44:
                return onto.C43_C44_REF
            if 45 <= int(code2) <= 49:
                return onto.C45_C49_REF
            if int(code2) == 50:
                return onto.C50_C50_REF
            if 51 <= int(code2) <= 58:
                return onto.C51_C58_REF
            if 60 <= int(code2) <= 63:
                return onto.C60_C63_REF
            if 64 <= int(code2) <= 68:
                return onto.C64_C68_REF
            # if int(code2) == 71:
                # return onto.C71_REF 
            if 69 <= int(code2) <= 72:
                return onto.C69_C72_REF
            if 73 <= int(code2) <= 75:
                return onto.C73_C75_REF
            if 76 <= int(code2) <= 80:
                return onto.C76_C80_REF
            if 81 <= int(code2) <= 96:
                return onto.C81_C96_REF
            if code2 == "7A":
                return onto.C7A_C7A_REF
            if code2 == "7B":
                return onto.C7B_C7B_REF
        if code1 == "D":
            if 0 <= int(code2) <= 9:
                return onto.D00_D09_REF
            if 10 <= int(code2) <= 36:
                return onto.D10_D36_REF
            if 37 <= int(code2) <= 48:
                return onto.D37_D48_REF
            if int(code2) == 49:
                return onto.D49_D49_REF
            if code2 == "3A":
                return onto.D3A_D3A_REF
        return 0 # error case

    
    ## --------------------- MAIN FUNCTION ---------------------
    def create_instances(data, 
                         patient_id_col='LINKNUMBER', 
                         tumour_id_col='MERGED_TUMOUR_ID',
                         tumour_icd10_col = 'SITE_ICD10_O2',
                         tumour_behaviour_col='BEHAVIOUR_ICD10_O2',
                         regimen_id_col = 'MERGED_REGIMEN_ID'):
        '''
        Mapping instances of data to individuals in the ontology.
        Optional parameters are PatientID, TumourID, Tumour behaviour, RegimenID columns
        '''

        for index, row in data.iterrows():
            # Create a new patient instance, but checks if patient has been created before
            patient_search = onto.search(PatientID = str(row[patient_id_col])+"*")
            if not patient_search:
                today = datetime.date.today()
                yearBorn = datetime.date(today.year-row['AGE'],1,1).year
                vital = row['NEWVITALSTATUS']
                thisPatient = onto.Patient(PatientID = [row[patient_id_col]], ## equivalent of NHS number 
                                            DateOfBirth = [yearBorn],
                                            VitalStatus = [vital],
                                            PrimaryDiagnosis = [row['PRIMARY_DIAGNOSIS']], ## patient primary tumour icd10
                                            Sex = [row['SEX']]
                                            )
            else:
                thisPatient = patient_search[0]
            i.patients.append(thisPatient)

            # Create a new tumour instance, also checks if tumour has been created before
            tumour_search = onto.search(TumourID = str(row[tumour_id_col])+"*")
            if not tumour_search:
                thisTumour = onto.Tumour(TumourID = [row[tumour_id_col]],
                                            DiagnosisDate = [row['DIAGNOSISDATEBEST']],
                                            ICD10_Code = [row[tumour_icd10_col]], ## tumour icd10
                                            has_behaviour_code = [onto_behaviour_code(onto, row[tumour_behaviour_col])], # behaviour code
                                            belongs_to_patient = [thisPatient],
                                            has_tumour_reference = [tumour_icd10_code(onto, row[tumour_icd10_col])]
                                            )
            else:
                thisTumour = tumour_search[0]
            i.tumours.append(thisTumour)

            # Create a new regimen instance, doesn't need to check if been created before, as new regimen is new row.
            thisRegimen = onto.Regimen(RegimenID = [row[regimen_id_col]], 
                                        treats = [thisTumour]
                                        )
            i.regimens.append(thisRegimen)

            # Create new drug instances in a for loop using names, then all drugs part of this regimen
            create_drug_instances(row['MAPPED_REGIMEN'], thisRegimen)
    
    # ----------- CREATING INSTANCES FUNCTION CALLED -----------------
    create_instances(data_to_map)