import json
from turtle import title
import pandas as pd

from requests import Session
from .core import PyDEEN
from pydeen.utils import CryptUtil, CryptEngine, FileTransferUtil
from pydeen.menu import  MenuSelection, MenuAction, UserInput

class Base:
    """
        Abstract base class
    """

    BASE_PROP_TYPE = "type"
    BASE_PROP_PROP = "properties"
    BASE_PROP_KEY  = "key"
    BASE_PROP_DESCRIPTION = "description" 

    def __init__(self) -> None:
        self.type = "pydeen.Base"
        self._properties = {}
        self.debug = False
        self.interactive = False
        self.last_error = None
        self.menu_title:str="PyDEEN Menu"

    def __repr__(self) -> str:
        return self.type

    def get_type(self) -> str:
        if self.type == None:
            return type(self)
        else:
            return self.type

    def trace(self, msg):
        if self.debug == True:
            print("DEBUG:", msg)
        
        try:
            PyDEEN.get_logger(self.get_type()).debug(msg)
        except Exception as exc:
            print(f"error while write to log: {type(exc)} - {exc}")    

    def info(self, msg):
        if self.debug == True or self.interactive == True:
            print("INFO:", msg)

        try:
            PyDEEN.get_logger(self.get_type()).info(msg)
        except Exception as exc:
            print(f"error while write to log: {type(exc)} - {exc}")    

    def warning(self, msg):
        if self.debug == True or self.interactive == True:
            print("WARNING:", msg)

        try:
            PyDEEN.get_logger(self.get_type()).warning(msg)
        except Exception as exc:
            print(f"error while write to log: {type(exc)} - {exc}")    

    def error(self, msg):
        if self.debug == True  or self.interactive == True:
            print("ERROR:", msg)

        self.last_error = msg    

        try:
            PyDEEN.get_logger(self.get_type()).error(msg)
        except Exception as exc:
            print(f"error while write to log: {type(exc)} - {exc}")    

    def get_last_error(self) -> str:
        return self.last_error

    def reset_last_error(self):
        self.last_error = None    
    
    def get_properties(self):
        return self._properties

    def set_property(self, name, value):
        if value == None or value == "":
            self._properties.pop(name, None)
        else:        
            self._properties[name] = value

    def get_property(self, name, default=None):
        if name in self._properties.keys():
            value = self._properties[name]
            value_type = type(value)
            if value_type == dict:
                engine_key = value[CryptEngine.PROP_ENGINE]
                engine = CryptUtil.get_engine(engine_key)        
                return engine.decode(value) 
            else:
                return value 
        else:
            return default

    def get_type(self) -> str:
        return self.type

    def get_key(self) -> str:
        return self.get_property(Base.BASE_PROP_KEY)

    def get_description(self) -> str:
        return self.get_property(Base.BASE_PROP_DESCRIPTION)

    def set_key(self, desc:str):
        self.set_property(Base.BASE_PROP_DESCRIPTION, desc)    

    def get_config(self):
        return self._properties

    def get_config_file_name(self, filename) -> str:
        if filename.find(".") > 0:
            return filename
        else:
            return filename + "." + self.type + ".cfg"   

    def set_config(self, config):
        self._properties = config    

    def save_config(self, filename) -> bool:
        try:
            config = self.get_config()
            if config == None:
                return False

            with open(self.get_config_file_name(filename), "w") as file:
                file.write(json.dumps(config))
            return True         
        except Exception as exc:
            self.error(f"Error while saving config: {type(exc)} - {exc}")
            return False
        

    def load_config(self, filename) -> bool:    
        try:    
            json_string = ""
            with open(self.get_config_file_name(filename),"r") as file:
                for line in file:
                    if json_string == "":
                        json_string = line
                    else:    
                        json_string += "\n" + line
            
            json_obj = json.loads(json_string)
            return self.set_config(json_obj)
        except Exception as exc:
            self.error(f"Error while loading config: {type(exc)} - {exc}")
            return False


    def menu_get_title(self) -> str:
        if self.menu_title != None:
            return self.menu_title
        else:    
            return "PyDEEN Menu"

    def menu_get_entries(self, prefilled:dict=None) -> dict:
        """
        Creates a context oriented menu for 'menu()'
        """
        if prefilled == None:
            return {}
        else:
            return prefilled        

    def menu_process_selection(self, selected:str, text:str=None):
        """
        Processes the user input from 'menu()'
        """
        if text == None:
            print(f"Selected menu {selected} not handled")
        else:    
            print(f"Selected menu '{text}' (code:{selected} not handled")

    def menu(self):
        """
        This function created an individual menu for the context object.
        See function 'menu_get_entries' and 'menu_process_selection' too.
        """


        # prepare      
        title = self.menu_get_title()
        self.trace(f"Menu {title} entered")
        saved_interactive = self.interactive
        self.interactive = True

        # menu loop
        valid = True
        while valid == True:
            
            # build main menu    
            entries = self.menu_get_entries()
            if entries == None or len(entries) == 0:
                print("This object has no menu")
                return False

            # show menu            
            action = MenuSelection(title, entries, True, False).show_menu()
            if action.is_quit_entered():
                valid = False
            else:
                try:
                    selected = action.get_selection()
                    menu_text = entries[selected]
                    self.menu_process_selection(selected, menu_text)    
                except Exception as exc:
                    print("Errors occured:", type(exc), exc)
            
        # cleanup and exit
        self.interactive = saved_interactive




class Auth(Base):
    """
        abstract authentification
    """

    AUTH_TYPE_NONE  = "None"
    AUTH_TYPE_BASIC = "Basic"

    AUTH_PROP_TYPE = "type"
    AUTH_PROP_USER = "user"
    AUTH_PROP_PASS = "password"


    def __init__(self) -> None:
        Base.__init__(self)
        self.type = "pydeen.Auth"

    def get_config(self):
        return self._properties

    def init_from_config(self, type, config:dict) -> bool:
        # have to be redefined
        self._properties = {}
        return False

    def set_config(self, config:dict) -> bool:
        
        self._properties = {}
        if Auth.AUTH_PROP_TYPE in config.keys():
            type = config[Auth.AUTH_PROP_TYPE]
        else:
            type = Auth.AUTH_TYPE_NONE     
        
        return self.init_from_config(type, config)

    def get_auth_type(self) -> str:
        type = self.get_property(Auth.AUTH_PROP_TYPE)
        if type == None:
            type = Auth.AUTH_TYPE_NONE

    def get_auth_headers(self) -> dict:
        return None      

    def get_auth_for_request(self):
        return None

    def get_auth_for_requests_session(self) -> Session:
        return None


class Backend(Base):
    """
        abstract enterprise backend with properties
    """
    # static constants
    BACKEND_PROP_NAME       = "name"
    BACKEND_PROP_AUTH       = "auth"
    BACKEND_PROP_HOST       = "host"
    BACKEND_PROP_PROTOCOL   = "protocol"
    BACKEND_PROP_TENANT     = "tenant"
    BACKEND_PROP_PORT       = "port"
    BACKEND_PROP_PATH       = "path"
    BACKEND_PROP_URL        = "url"
    BACKEND_PROP_LANGUAGE   = "language"


    def __init__(self, name, auth:Auth=None) -> None:
        Base.__init__(self)
        self.name = name
        self.type = "pydeen.Backend"
        self.params = {}

        if auth == None:
            self._auth = Auth()
        else:
            self._auth = auth

    def get_name(self):
        return self.name
        
    def set_auth_info(self, auth:Auth):
        self._auth = auth

    def set_auth_basic(self, user, password):
        self._auth = Auth()
        self._auth.set_basic_auth(user, password)

    def get_auth_info(self) -> Auth:
        return self._auth

    def get_params(self):
        return self.params

    def is_auth_info_available(self) -> bool:
        """
            checks if an authorization information is given
        """
        if self._auth == None or self._auth.get_auth_type() == Auth.AUTH_TYPE_NONE:
            return False
        else:
            return True    

    def get_auth_for_request(self):
        return None    

    def set_connection(self, host, port="", protocol="", tenant="", path="", language=""):
        self.set_property(Backend.BACKEND_PROP_HOST, host)
        self.set_property(Backend.BACKEND_PROP_PORT, port)
        self.set_property(Backend.BACKEND_PROP_PROTOCOL, protocol)
        self.set_property(Backend.BACKEND_PROP_TENANT, tenant)
        self.set_property(Backend.BACKEND_PROP_PATH, path)
        self.set_property(Backend.BACKEND_PROP_LANGUAGE, language)

    def get_config(self):
        json_obj = {}
        json_obj[Backend.BASE_PROP_TYPE] = self.type
        json_obj[Backend.BASE_PROP_PROP] = self._properties
        json_obj[Backend.BACKEND_PROP_NAME] = self.name
        json_obj[Backend.BACKEND_PROP_AUTH] = self._auth.get_config()
        return json_obj

    def set_config(self, config) -> bool:

        # set main fields
        self.name = config[Backend.BACKEND_PROP_NAME]
        self.type = config[Backend.BASE_PROP_TYPE]
        self._properties = config[Backend.BASE_PROP_PROP]

        # check auth info
        self._auth = Auth()
        auth_config = config[Backend.BACKEND_PROP_AUTH]
        #print("Read AuthConfig", auth_config)
        if self._auth.set_config(auth_config) == False:
            print("no auth information available for backend")

        # result
        return True
        
class Connector(Base):
    """
        abstract connector to an backend system
    """
    def __init__(self, backend) -> None:
        Base.__init__(self)
        self.type = "pydeen.Connector"
        self.backend = backend
        self.params = {}

    def __repr__(self) ->str:
        return f"{self.type} to {self.backend}"

    def get_backend(self) -> Backend:
        return self.backend

class EntityMetaInfo(Base):
    def __init__(self) -> None:
        super().__init__()
        self.type = "EntityMetaInfo"

    def get_columns(self) -> list:
        return None
class Result(Base):

    MENU_DISPLAY_RAW        = "result_display_raw"
    MENU_SAVE_RAW           = "result_save_raw"
    MENU_DISPLAY_COLS       = "result_display_cols"

    def __init__(self, result) -> None:
        super().__init__()
        self.result = result 
        self.result_name:str = None   
        self.type = "pydeen.Result"
        self.columns = None
        self.entityMetaInfo:EntityMetaInfo=None
        self.menu_title = "Result - Menu"

    def set_entity_metainfo(self, metainfo):
        self.entityMetaInfo = metainfo

    def get_name(self) -> str:
        if self.result_name != None:
            return self.result_name
        else:
            return "unknown"

    def set_name(self, name):
        self.result_name = name

    def get_result_raw(self):
        return self.result

    def is_list(self) -> bool:
        if self.result == None:
            return False

        if type(self.result) == "<class 'list'>":
            return True

    def is_list_of_dict(self) -> bool:
        if self.is_list() == False or self.is_empty() == True:
            return False

        if type(self.result[0]) == "<class 'dict'>":
            return True

    def is_empty(self) -> bool:
        if self.result == None:
            return True

        if self.is_list() == True:
            if self.result.len() == 0:
                return True                    
        
        return False

    def get_columns(self) -> list:
        # check metainfo
        result = None
        if self.entityMetaInfo != None:
            result = self.entityMetaInfo.get_columns()

        if result != None:
            return result
        
        # cols from data cached?
        if self.columns != None:
            return self.columns
        
        # check workaround
        if self.is_list_of_dict() == False:
            return None
        else:
            result = []
            for name in self.result[0].keys():
                result.append(name)
        # workaround active
        self.columns = result
        return result             

    def get_count(self) -> int:        
        if self.result == None:
            return 0

        try:
            return len(self.result)
        except:
            print("ERROR COUNT")
            return 0    

    def get_result_as_pandas_df(self, type_mapping:bool=True) -> pd.DataFrame:
        # check result
        if self.is_list_of_dict() == False:
            self.error("invalid result type to convert to pandas dataframe")
            return None
        
        # get result
        raw  = self.get_result_raw()
        cols = self.get_columns()
        if cols == None or len(cols) == 0 or raw == None or len(raw) == 0:
            self.error("invalid result data to convert to pandas dataframe")
            return None

        # prepare pandas
        data = []
        for record in raw:
            entry = []
            for col in cols:
                raw_value = record[col]
                value = self.convert_raw_value(col, raw_value)
                entry.append(value)
            data.append(entry)    

        # create dataframe
        df = pd.DataFrame(data,columns=cols)
        return df

    def convert_raw_value(self, column, value):
        return value   

    def menu_get_entries(self, prefilled: dict = None) -> dict:
        # check
        entries = super().menu_get_entries(prefilled)
        if self.is_empty( ) == True:
            return entries
        
        # prepare
        count = self.get_count()
        columns = self.get_columns()

        entries[Result.MENU_DISPLAY_RAW] = "Display raw data"
        entries[Result.MENU_SAVE_RAW] = "Save raw data"
        if columns != None and len(columns) > 0:
            entries[Result.MENU_DISPLAY_COLS] = "Display column names"
        
        return entries

    def menu_process_selection(self, selected: str, text: str = None):
        try:
            if selected == Result.MENU_DISPLAY_RAW:
                print(self.get_result_raw())
            elif selected == Result.MENU_SAVE_RAW:
                content = json.dumps(self.result)
                if self.entityMetaInfo != None:
                    name = self.entityMetaInfo.get_description()
                else:
                    name = "result"    
                FileTransferUtil().enter_filename_and_save_text("Save result as text", name, content, with_datetime_prefix=True, extension="txt")
            elif selected == Result.MENU_DISPLAY_COLS:
                columns = self.get_columns()
                print(f"columns: {len(columns)}")
                for col in columns:
                    print(col)
            else:
                return super().menu_process_selection(selected, text)
        except Exception as exc:
            print("Errors occured:", type(exc), exc)


    # def menu(self):
    #     # check
    #     if self.is_empty( ) == True:
    #         print("Empty result - no menu possible")
    #         return False
    #     else:
    #         count = self.get_count()
    #         columns = self.get_columns()

    #     # build menu
    #     entries = {}
    #     entries[Result.MENU_DISPLAY_RAW] = "Display raw data"
    #     if columns != None and len(columns) > 0:
    #         entries[Result.MENU_DISPLAY_COLS] = "Display column names"


    #     # show menu            
    #     valid = True
    #     while valid:
    #         action = MenuSelection(f"Result (count {count})- Menu", entries, True, False).show_menu()
    #         if action.is_quit_entered():
    #             valid = False
    #         else:
    #             try:
    #                 selected = action.get_selection()
    #                 if selected == Result.MENU_DISPLAY_RAW:
    #                     print(self.get_result_raw())
    #                 if selected == Result.MENU_DISPLAY_COLS:
    #                     print(f"columns: {len(columns)}")
    #                     for col in columns:
    #                         print(col)
    #                 else:
    #                     print("unknown menu action")
    #             except Exception as exc:
    #                 print("Errors occured:", type(exc), exc)
    #                 return False
        
    #     return True


class Request(Base):

    def __init__(self) -> None:
        super().__init__()
        self.result = None
        self.type = "pydeen.Request"

    def get_result(self) -> Result:
        return self.result


