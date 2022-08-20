"""
    SAP ABAP DEEB Plugin Connector
"""

from pydeen.types import Backend, Connector, Auth, Result
from pydeen.http import HTTPConnector, HTTPBackend, HTTPRequest
from pydeen.menu import  MenuSelection, MenuAction, UserInput
from pydeen.sap_abap import SAPAbapHttpBackend
from datetime import datetime, timedelta, timezone
import pandas as pd 

import requests
import json
import re
import sys

class SAPAbapDeebResult(Result):
    def __init__(self, result, metainfo=None) -> None:
        super().__init__(result)
        self.type = "pydeen.SAPAbapDeebResult"
        self.metainfo = metainfo


class SAPAbapDeebConnector(HTTPConnector):
    
    # static constants
    MENU_PING               = "ping"
    MENU_SEARCH_TABLE       = "search_table"
    MENU_SEARCH_VIEW        = "search_view"
    MENU_SEARCH_CDS         = "search_cds"
    MENU_SQL_SELECT         = "sql_select"
    MENU_RESULT_RAW         = "result_raw"
    MENU_RESULT_PANDAS      = "result_pandas"
    MENU_RESET              = "reset"
    
    def __init__(self, backend:Backend=None, url_or_endpoint:str=""):
        url = url_or_endpoint
        if url == None or len(url) == 0:
            url = '/sap/bc/bsp/sap/zdeeb_ws'
            
        super().__init__(backend, url)
        self.type = "pydeen.SAPAbapDeebConnector"
        self.menu_result   = None
        self.max_rec = 10000
        self.last_input = None
        

    def menu_action_reset(self):
        self.menu_result = None
        print("Menu context cleared.")

    def menu_action_ping(self):
        
        success, response, http_code = self.ping()

        if success == True:
            print(response)
        else:
            print(f"Ping failed: http code {http_code} - {response}")    


    def menu_action_search_table(self):
        input = UserInput("Enter Wildcard for table (use '*')", self.last_input).get_input(empty_allowed=True)
        if input == None:
            return

        result = self.search_tables(input)
        if result == None or len(result) == 0:
            print("No results")
        else:
            count = len(result)
            print(f"{count} tables found.")
            for record in result:
                #print(f"{record[0]} - {record[1]} ({record[2]})")
                print(record)

    def menu_action_search_cds(self):
        input = UserInput("Enter Wildcard for cds (use '*')", self.last_input).get_input(empty_allowed=True)
        if input == None:
            return

        result = self.search_cds_view(input)
        if result == None or len(result) == 0:
            print("No results")
        else:
            count = len(result)
            print(f"{count} cds views found.")
            for record in result:
                #print(f"{record[0]} - {record[1]} ({record[2]})")
                print(record)

    def menu_action_sql_select(self):
        input = UserInput("Enter SQL Statement", self.last_input).get_input(empty_allowed=True)
        if input == None:
            return

        self.menu_result = None
        self.last_input = input

        success, response, http_code = self.execute_sql(input)
        if success == True:
            #result = json.loads(response)
            #self.menu_result = SAPAbapDeebResult(result)
            self.menu_result = self.sql_response_to_result(response)
            count = self.menu_result.get_count()
            cols  = self.menu_result.get_columns()
            print(f"SQL select finished: {count} records in {len(cols)} columns")
            print(cols)
        else:
            print(f"SQL select failed: http code {http_code} - {response}")   

    def menu(self):        
        valid = True
        while valid == True:
            
            # build main menu    
            entries = {}
            entries[SAPAbapDeebConnector.MENU_PING] = "Ping ABAP Backend DEEB Service"
            entries[SAPAbapDeebConnector.MENU_SEARCH_TABLE] = "Search table"
            entries[SAPAbapDeebConnector.MENU_SEARCH_CDS] = "Search cds view"
            entries[SAPAbapDeebConnector.MENU_SQL_SELECT] = "Excecute SQL Select Statement"

            if self.menu_result != None:
                    entries[SAPAbapDeebConnector.MENU_RESULT_RAW] = f"Display current result as raw data"
                    entries[SAPAbapDeebConnector.MENU_RESULT_PANDAS] = f"Display current result as pandas dataframe"

            entries[SAPAbapDeebConnector.MENU_RESET] = "Reset menu context"

            # show menu            
            action = MenuSelection("SAP NetWeaver ABAP DEEB Connector - Menu", entries, True, False).show_menu()
            if action.is_quit_entered():
                valid = False
            else:
                try:
                    selected = action.get_selection()
                    if selected == SAPAbapDeebConnector.MENU_RESULT_RAW:
                        print(self.menu_result.get_result_raw())
                    elif selected == SAPAbapDeebConnector.MENU_RESULT_PANDAS:
                        df:pd.DataFrame = self.menu_result.get_result_as_pandas_df()
                        print(df)    
                    elif selected == SAPAbapDeebConnector.MENU_RESET:
                        self.menu_action_reset()
                    elif selected == SAPAbapDeebConnector.MENU_PING:
                        self.menu_action_ping()    
                    elif selected == SAPAbapDeebConnector.MENU_SEARCH_TABLE:
                        self.menu_action_search_table()
                    elif selected == SAPAbapDeebConnector.MENU_SEARCH_CDS:
                        self.menu_action_search_cds()
                    elif selected == SAPAbapDeebConnector.MENU_SQL_SELECT:
                        self.menu_action_sql_select()    
                    else:
                        print("unknown menu action")
                except Exception as exc:
                    print("Errors occured:", type(exc), exc)

    def ping(self):
        # build a new request
        request = self.create_request()        
        # prepare params
        params = {}

        client  = self.backend.get_client()
        if client != None:
            params[SAPAbapHttpBackend.HTTP_PARAM_SAPCLIENT] = client

        # call sap service api
        self.trace("Call sap for DEEB Ping")
        http_code = request.get(f"{self.endpoint}/ping", params)
        response = request.get_response_text()
        if http_code < 200 or http_code > 299:
            self.trace(f"invalid answer - return code {http_code}") 
            return False, response, http_code
        else:
            self.trace("Ping OK")
            return True, response, http_code            
               
    def sql_response_to_result(self, response: str) -> Result:
        try:
            result = json.loads(response)
            return SAPAbapDeebResult(result)
        except Exception as exc:
            self.error(f"Errors occured while convert sql response to Result: {type(exc)} - {exc}")
            return None   
    
    def execute_sql(self, sql:str, max_rec:int=0):
        # build a new request
        request = self.create_request()        
        
        payload = {}
        payload["SQL"] = sql 
        
        max_records = max_rec
        if max_records <= 0:
            max_records = self.max_rec

        if max_records > 0:
            payload["MAX_RECORDS"] = max_records
        
        # prepare params
        params = {}
        client  = self.backend.get_client()
        if client != None:
            params[SAPAbapHttpBackend.HTTP_PARAM_SAPCLIENT] = client

        # call sap service api
        self.trace("Call sap for DEEB SQL Select")
        
        http_code = request.post(json.dumps(payload), f"{self.endpoint}/sql_select", params)
        response = request.get_response_text()
        if http_code < 200 or http_code > 299:
            self.trace(f"invalid answer - return code {http_code}") 
            return False, response, http_code
        else:
            self.trace("SQL Select OK")
            return True, response, http_code   

    def search_tables(self, wildcard:str) -> list:
        try:
            if wildcard == None:
                return None
            search_str = wildcard.replace("*", "%")

            #sql_request = f"SELECT m~tabname as table_name, t~ddtext  as description, t~DDLANGUAGE as language FROM dd02l AS m LEFT OUTER JOIN dd02t AS t ON m~tabname = t~tabname and m~as4local = t~as4local and m~as4vers = t~as4vers WHERE m~tabname LIKE '{search_str}' OR t~ddtext LIKE '{search_str}' ORDER BY m~tabname"
            sql_request = f"SELECT tabname as table_name FROM dd02l where tabname like '{search_str}' order by tabname"

            success, sql_response, http_code = self.execute_sql(sql_request, self.max_rec)
            if success == False:
                return None

            result = []    
            if sql_response != None:
                json_result = json.loads(sql_response)
                for line in json_result:
                    table = line["TABLE_NAME"]
                    table = table.replace("\\/", "/")
                    result.append(table)

            return result
        except Exception as exc:
            self.error(f"Error while selecting tables with wildcard {wildcard}: {type(exc)} - {exc}")
            return None    

    def search_cds_view(self, wildcard:str) -> list:
        try:
            if wildcard == None:
                return None
            search_str = wildcard.replace("*", "%")

            #sql_request = f"SELECT m~tabname as table_name, t~ddtext  as description, t~DDLANGUAGE as language FROM dd02l AS m LEFT OUTER JOIN dd02t AS t ON m~tabname = t~tabname and m~as4local = t~as4local and m~as4vers = t~as4vers WHERE m~tabname LIKE '{search_str}' OR t~ddtext LIKE '{search_str}' ORDER BY m~tabname"
            sql_request = f"SELECT OBJ_NAME as CDS_NAME FROM TADIR where PGMID = 'R3TR' and OBJECT = 'DDLS' and OBJ_NAME like '{search_str}' order by OBJ_NAME"

            success, sql_response, http_code = self.execute_sql(sql_request, self.max_rec)
            if success == False:
                return None

            result = []    
            if sql_response != None:
                json_result = json.loads(sql_response)
                for line in json_result:
                    table = line["CDS_NAME"]
                    table = table.replace("\\/", "/")
                    result.append(table)

            return result
        except Exception as exc:
            self.error(f"Error while selecting cds views with wildcard {wildcard}: {type(exc)} - {exc}")
            return None    


    def get_current_result(self) -> Result:
        return self.menu_result

    def get_current_result_as_pandas_df(self) -> Result:
        try:
            return self.menu_result.get_result_as_pandas_df()
        except:
            return None    
