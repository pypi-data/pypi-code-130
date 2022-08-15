# -*- coding: utf-8 -*-
    
import requests
from io import StringIO
import pandas as pd
import json
import time


class YMAPIRequest:
    """
    Sends a single request to Yandex Metrica API with given parameters
    """
    
    def __init__(self, token, params):
        self.token = token
        self.params = params
        self.response_code = 0
        self.response_message = ""
        self.error_type = ""
        self.data = pd.DataFrame()
       
    def perform_request(self, limit, offset):
        self.params.update({"limit":limit, "offset":offset})
        
        r = requests.get('https://api-metrika.yandex.ru/stat/v1/data.csv?', 
                         params=self.params,
                         headers={"Authorization": "OAuth {}".format(self.token)})
        self.response_code = r.status_code
        response_data = r.text
        
        #Check for errors
        if self.response_code >= 400:
            #Error
            response = json.loads(response_data)
            self.response_message = response["message"]
            self.error_type = response["errors"][0]["error_type"]
        else:
            #Success
            self.response_message = "Success"
            df = pd.read_csv(StringIO(response_data), sep=",")
            #Delete row with totals
            if not df.empty:
                if df.iloc[0][0] == 'Итого и средние':
                    df.drop(index=df.index[0], axis=0, inplace=True)
            self.data = df
               
    
class YMAPILoader:
    """
    Downloads all data from Yandex Metrica API with given parameters
    """
    
    def __init__(self, token, params, attempts=10):
       self.token = token
       self.params = params
       self.limit = 100000   # 100 000 is max
       self.max_number_of_attempts = attempts
       self.data = pd.DataFrame()
                 
    def load_all_data(self):
        rows = self.limit
        offset = 1
        attempt = 1
        
        req = YMAPIRequest(self.token, self.params)
        
        while rows == self.limit and attempt <= self.max_number_of_attempts:
            
            # print("Attempt: {}".format(attempt))################
            req.perform_request(self.limit, offset)
            # print("Response: {}".format(req.response_code))################
            
            if req.response_message == "Success":
                #Data obtained successfully
                
                df_new = req.data
                # print(df_new)#############
                self.data = pd.concat([self.data, df_new])
                rows = len(df_new.index)
                
                #Move to the next chunk of data
                offset += self.limit
                
                #Reset a number of unsuccessfull attempts after a successfull one
                attempt = 1
                
            elif req.error_type in ('backend_error', 'query_error'):
                #Request returned an error and can be repeated 
                
                if attempt < self.max_number_of_attempts:
                    #Wait and try again if attempts limit was not achieved yet
                    time.sleep(2*attempt)
                    attempt += 1
                    
                else:
                    #Remove incomplete data and show an error after achieving the attempts limit
                    self.data = self.data.iloc[0:0]
                    print("API Error {}: {}".format(req.response_code, req.response_message))
            else:
                #Request returned a critical error and should be stoped
                
                attempt = self.max_number_of_attempts + 1
                self.data = self.data.iloc[0:0]
                print("API Error {}: {}".format(req.response_code, req.response_message))
                               
    def save_data_to_excel(self, file_name, sheet_name='Sheet1'):
        #Save data to excel if it is not empty
        if not self.data.empty:
            self.data.to_excel(file_name, sheet_name, index=False)
        else:
            print('Saving data to excel... No data. Nothing to save.')
