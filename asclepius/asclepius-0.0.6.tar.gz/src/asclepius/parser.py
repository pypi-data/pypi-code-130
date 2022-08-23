import sys
sys.path.append(r'\\valuecare.local\fileserver\Algemeen\Automatisch testen\Python')
from parameters import HardCodedParameters

# import other dependencies
import re
import os
from numpy import nan as numpy_nan
from pandas import DataFrame, ExcelWriter, isnull, read_excel, concat

class KPI:
    def __init__(self, file_path: str) -> None:
        # open the KPI file and read it's content
        file = open(file_path, 'r')
        f = file.read()
        file.close()
        
        # search for the KPI information
        self.set_attributes(f)

        # Value fields moeten apart worden gevonden
        self.set_value_fields_attribute(file_path)
        return None

    def __del__(self):
        pass
    
    def set_attributes(self, f: str) -> None:
        self.roosterstap_nr = self.pattern_finder(f, 'roosterstap_nr')
        self.titel = self.pattern_finder(f, 'titel')
        self.paginanaam, self.verborgen_filters = self.pagename_hidden_filter_finder(f)
        self.zichtbare_filters = self.visible_filter_finder(f)
        self.facetten = self.facet_finder(f)
        return None

    def set_value_fields_attribute(self, file_path: str) -> None:
        self.value_fields = self.value_fields_finder(file_path)
        return None

    
    def pattern_finder(self, f: open, kpi_attribute: str):
        ref_pattern = re.compile(HardCodedParameters.kpi_pattern_dict[kpi_attribute])
        match_obj = re.search(ref_pattern, f)
        if type(match_obj) == type(None):
            return ""
        else:
            return match_obj.group(1)
    
    def pagename_hidden_filter_finder(self, f: open):
        ref_pattern = re.compile(HardCodedParameters.kpi_pattern_dict['paginanaam'])
        match_obj = re.search(ref_pattern, f)
        if type(match_obj) == type(None):
            return "", ""
        else:
            return match_obj.group(1), match_obj.group(2)
    
    def visible_filter_finder(self, f: open) -> str:
        ref_pattern = re.compile(HardCodedParameters.kpi_pattern_dict['zichtbare_filters'])
        match_list = re.findall(ref_pattern, f)
        visible_filters = ""
        if len(match_list) == 0:
            pass
        else:
            for item in match_list:
                if len(visible_filters) == 0:
                    visible_filters += f"{item[0]} = {item[1]}"
                else:
                    visible_filters += f", {item[0]} = {item[1]}"
        return visible_filters
    
    def facet_finder(self, f: open) -> str:
        ref_pattern = re.compile(HardCodedParameters.kpi_pattern_dict['facets'])
        match_list = re.findall(ref_pattern, f)
        facets = ""
        for item in match_list:
            if len(facets) == 0:
                facets += item
            else:
                facets += f", {item}"
        return facets

    def value_fields_finder(self, file_path) -> None:
        # regex pattern
        ref_pattern_1 = re.compile(HardCodedParameters.kpi_pattern_dict['value_fields_start'])
        ref_pattern_2 = re.compile(HardCodedParameters.kpi_pattern_dict['value_fields'])
        ref_pattern_3 = re.compile(HardCodedParameters.kpi_pattern_dict['value_fields_end'])
        
        # read file line by line
        file = open(file_path, 'r')
        lines = file.readlines()
        
        in_value_fields = False
        value_fields_list = []
        for line in lines:
            # check of we in de value fields sectie zijn
            if in_value_fields:
                # check of deze regel niet het einde van de value fields is
                if re.search(ref_pattern_3, line):
                    in_value_fields = False
                # zo niet dan is het een value field
                else:
                    match_obj = re.search(ref_pattern_2, line)
                    value_fields_list.append(match_obj.group(1).strip())
                    
            # als we nog niet in de value fields sectie zijn kijken
            # we of die sectie start op deze regel
            elif re.search(ref_pattern_1, line):
                in_value_fields = True
            else:
                pass

        # duplicaten verwijderen
        value_fields_list = list(set(value_fields_list))

        # output als string
        value_fields = ""
        for item in value_fields_list:
            if len(value_fields) == 0:
                value_fields += item
            else:
                value_fields += f", {item}"
        return value_fields

class KPIParser:
    def __init__(self):
        pass
    
    def from_file(self, file: str, return_df: bool = False):
        kpi = KPI(file)
        if return_df:
            return kpi
        else:
            self.kpi_to_excel(kpi)
            return None

    def from_folder(self, folder: str):
        # kijk welke bestanden er in de map staan
        files = os.listdir(folder)

        # converteer de gevonden namen naar paths
        paths = [os.path.join(folder, file) for file in files]

        # creeer DataFrame
        kpi_df = DataFrame({'Roosterstapnummer': [], 'KPI titel': [], 'Paginanaam': [], 'Verborgen filters': [], 'Zichtbare filters': [], 'Facetten': [], 'Value fields': []})

        # 
        for path in paths:
            try:
                kpi = KPI(path)
            except:
                print(f'Fout bij het parsen van {path}')
                continue
            new_line = DataFrame({'Roosterstapnummer': kpi.roosterstap_nr, 'KPI titel': kpi.titel, 'Paginanaam': kpi.paginanaam, 'Verborgen filters': kpi.verborgen_filters, 'Zichtbare filters': kpi.zichtbare_filters, 'Facetten': kpi.facetten, 'Value fields': kpi.value_fields}, index = [0])
            kpi_df = concat((kpi_df, new_line), ignore_index = True)
    

        with ExcelWriter(f'Metadata KPIs.xlsx') as writer:
            kpi_df.to_excel(writer, sheet_name = 'Metadata')

    def kpi_to_excel(self, kpi: KPI):
        kpi_df = DataFrame({'Roosterstapnummer': [], 'KPI titel': [], 'Paginanaam': [], 'Verborgen filters': [], 'Zichtbare filters': [], 'Facetten': [], 'Value fields': []})
        new_line = DataFrame({'Roosterstapnummer': kpi.roosterstap_nr, 'KPI titel': kpi.titel, 'Paginanaam': kpi.paginanaam, 'Verborgen filters': kpi.verborgen_filters, 'Zichtbare filters': kpi.zichtbare_filters, 'Facetten': kpi.facetten, 'Value fields': kpi.value_fields}, index = [0])
        kpi_df = concat((kpi_df, new_line), ignore_index = True)
        with ExcelWriter(f'Metadata {kpi.roosterstap_nr}.xlsx') as writer:
            kpi_df.to_excel(writer, sheet_name = 'Metadata')
        return None

    def explode_hidden_filters(self, input_df: DataFrame):
        df = input_df

        # Drop alle entries die geen verborgen filters hebben
        df = df.dropna(subset = ['Verborgen filters'])

        # splits op de ' and '
        dummy = df['Verborgen filters']
        dummy = dummy.str.split(pat = r' and | or ')
        df['Verborgen filters dummy'] = dummy

        # elk item in de lijst wordt een eigen entry in het DataFrame
        df = df.explode('Verborgen filters dummy', ignore_index = True)
        

        # Importeer het ref pattern uit HardCodedParameters
        ref_pattern = re.compile(HardCodedParameters.kpi_pattern_dict['verborgen_filters'])
        
        # re om de facet naam, het data format en de waarde te splitsen
        for index, entry in df.iterrows():

            # Lees de entry uit
            f = entry['Verborgen filters dummy']

            try:
                match_obj = re.search(ref_pattern, f)
            except Exception as ex:
                print(f'Probleem met explode_hidden_filters in regel {index}.')
                print(ex)
                print('Entry:', entry['KPI titel'], 'value:', f)
                continue
            
            if match_obj:
                # gevonden waardes toevoegen aan het DataFrame
                df.at[index, 'Facetnaam'] = match_obj.group(1)
                df.at[index, 'Data format'] = match_obj.group(2)
                df.at[index, 'Value'] = match_obj.group(3).replace('"', '')
            else:
                pass
        
        df['Functie'] = ['Verborgen filter' for i in range(len(df))]
        return df

    def explode_facetten(self, input_df: DataFrame):
        df = input_df
        
        dummy = df['Facetten']
        dummy = dummy.str.split(pat = ', ')
        df['Facetnaam'] = dummy
        
        df = df.explode('Facetnaam', ignore_index = True)
        
        df['Functie'] = ['Zichtbare facetten' for i in range(len(df))]
        return df

    def explode_value_fields(self, input_df: DataFrame):
        df = input_df
        
        dummy = df['Value fields']
        dummy = dummy.str.split(pat = ', ')
        df['Facetnaam'] = dummy
        
        df = df.explode('Facetnaam', ignore_index = True)
        
        df['Functie'] = ['Value fields' for i in range(len(df))]
        return df

    def explode_visible_filters(self, input_df: DataFrame):
        df = input_df

        # Drop alle entries die geen zichtbare filters hebben
        df = df.dropna(subset = ['Zichtbare filters'])

        # splits op de ', '
        dummy = df['Zichtbare filters']
        dummy = dummy.str.split(pat = ', ')
        df['Zichtbare filters dummy'] = dummy
        
        # elk item in de lijst wordt een eigen entry in het DataFrame
        df = df.explode('Zichtbare filters dummy', ignore_index = True)

        ref_pattern = re.compile(HardCodedParameters.kpi_pattern_dict['zichtbare_filters'])
        
        # re om de facet naam, het data format en de waarde te splitsen
        for index, entry in df.iterrows():

            f = entry['Zichtbare filters dummy']

            try:
                match_obj = re.search(ref_pattern, f)
            except Exception as ex:
                print(f'Probleem met explode_visible_filters in regel {index}.')
                print('Entry:', entry['KPI titel'], 'value:', f)
                print(ex)

                continue
            
            if match_obj:
                # gevonden waardes toevoegen aan het DataFrame
                #df.at[index, 'Facetnaam'] = match_obj.group(1)
                #if match_obj.group(2):
                #    df.at[index, 'Data format'] = match_obj.group(2).strip('":{}')
                #else:
                #    df.at[index, 'Data format'] = ''
                #df.at[index, 'Value'] = match_obj.group(3).replace('"', '')

                # gevonden waardes toevoegen aan het DataFrame
                df.at[index, 'Facetnaam'] = match_obj.group(1)
                df.at[index, 'Data format'] = ''
                df.at[index, 'Value'] = match_obj.group(2)
            else:
                pass
        
        df['Functie'] = ['Zichtbaar filter' for i in range(len(df))]
        return df

    def splits_facetten(self, excel_file: str, to_excel: bool = False):
        # De KPI Metadata excell file inlezen
        df = read_excel(excel_file, index_col = 0)
        df.fillna(value = numpy_nan)
        
        # voeg nieuwe columns toe
        df = concat([df, DataFrame({'Facetnaam': [], 'Functie': [], 'Data format': [], 'Value': []}, dtype = str)])
        
        df1 = self.explode_hidden_filters(df)
        df2 = self.explode_facetten(df)
        df3 = self.explode_visible_filters(df)
        df4 = self.explode_value_fields(df)
        
        output_df = concat([df1, df2, df3, df4], axis = 0)
        
        output_df = output_df[['Roosterstapnummer', 'KPI titel', 'Paginanaam', 'Facetnaam', 'Functie', 'Data format', 'Value']]

        # output produceren
        if to_excel:
            with ExcelWriter('Facetten KPIs.xlsx') as writer:
                output_df.to_excel(writer, sheet_name = 'Facetten')
            return None
        else:
            output_df.to_csv('Facetten KPIs.csv')
            return None

    

