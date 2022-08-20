import pandas as pd

# returns a sorted list of options from a multi-select Affinity field
def extract_all_options_from_multiselect_field(dataframe: pd.DataFrame, multiselect_field: str, option_list: list(str)=[]):
    field_list = list(set(list(dataframe[multiselect_field].unique())))
    for entry in field_list:
        option_list += [x.strip() for x in str(entry).split("; ")]
    option_list = list(set(option_list))
    return option_list