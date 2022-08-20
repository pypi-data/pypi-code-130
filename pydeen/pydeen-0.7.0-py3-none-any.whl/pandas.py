"""
This module contains functions for integrating the pandas library
"""

from doctest import ELLIPSIS_MARKER
from pandas import DataFrame
from pydeen.menu import UserInput
from pydeen.types import Result
from pydeen.utils import FileTransferUtil

class PandasResultDataframe(Result):
    
    MENU_PANDAS_DISPLAY         = "pandas_display"
    MENU_PANDAS_INFO            = "pandas_info"
    MENU_PANDAS_HEAD_TAIL       = "pandas_head_tail"
    MENU_PANDAS_DESCRIBE        = "pandas_describe"
    MENU_PANDAS_DATATYPES       = "pandas_datatypes"
    MENU_PANDAS_VALUE_DIST      = "pandas_value_dist"
    MENU_PANDAS_SAVE_CSV        = "pandas_save_csv"


    def __init__(self, df:DataFrame, name:str) -> None:
        super().__init__(df)
        self.type = "pydeen.PandasResultDataframe"
        self.result_df:DataFrame = df 
        self.result_name:str = name
        self.menu_title = "Pandas Dataframe - Menu"

    def get_columns(self) -> list:
        try:
            return self.result_df.columns.tolist()
        except Exception as exc:
            self.trace(f"Error occured while determing columns of dataframe: {type(exc)} - {exc}")
            return super().get_columns()

    def is_empty(self) -> bool:
        try:
            if type(self.result_df) != None:
                return False
            else:
                return True
        except Exception as exc:
            print(type(exc), exc)
            return True

    def menu_get_entries(self, prefilled: dict = None) -> dict:
        entries = {} # NO SUPER MENU - super().menu_get_entries(prefilled)
        try:
            if self.is_empty() == False:
                entries[PandasResultDataframe.MENU_PANDAS_DISPLAY] = "Display dataframe"
                entries[PandasResultDataframe.MENU_PANDAS_INFO] = "Display dataframe info"
                entries[PandasResultDataframe.MENU_PANDAS_HEAD_TAIL] = "Display dataframe head/tail"
                entries[PandasResultDataframe.MENU_PANDAS_DESCRIBE] = "Describe dataframe"
                entries[PandasResultDataframe.MENU_PANDAS_DATATYPES] = "Display dataframe types"
                entries[PandasResultDataframe.MENU_PANDAS_VALUE_DIST] = "Show value distribution of column"
                entries[PandasResultDataframe.MENU_PANDAS_SAVE_CSV] = "Save datafrom to csv"
        except:
            self.trace("errors occured in pandas df menu")
        finally:
            return entries

    def menu_process_selection(self, selected: str, text: str = None):
        if selected == PandasResultDataframe.MENU_PANDAS_DISPLAY:
            print(self.result_df)
        elif selected == PandasResultDataframe.MENU_PANDAS_INFO:
            print(self.result_df.info())
        elif selected == PandasResultDataframe.MENU_PANDAS_HEAD_TAIL:
            print(self.result_df.head())
            print(self.result_df.tail())
        elif selected == PandasResultDataframe.MENU_PANDAS_DESCRIBE:
            print(self.result_df.describe())
        elif selected == PandasResultDataframe.MENU_PANDAS_DATATYPES:
            print(self.result_df.dtypes)
        elif selected == PandasResultDataframe.MENU_PANDAS_VALUE_DIST:
            columns = self.get_columns()
            selected = UserInput("Select column").get_selection_from_list("Show value distribution for dataframe column", columns)
            if selected != None:
                print(f"values of column {selected}:")
                print(self.result_df[selected].value_counts())   
        elif selected == PandasResultDataframe.MENU_PANDAS_SAVE_CSV:
            filename = FileTransferUtil().enter_filename_to_save("save current dataframe to csv", "dataframe", "csv", use_datetime_prefix=True)
            if filename != None:
                self.result_df.to_csv(filename,sep="\t")
        else:    
            return super().menu_process_selection(selected, text)    

