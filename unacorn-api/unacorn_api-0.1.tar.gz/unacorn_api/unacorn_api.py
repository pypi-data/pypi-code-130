import re
import json
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from nptdms import TdmsFile


class UnacornApi(): 
    
    def __init__(self, endpoint, username, password):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        request = requests.post(self.endpoint + "/login", data={'username': self.username, 'password': self.password})
        if request.status_code != 200:
            raise Exception(f"Status Code: {request.status_code}. Username/Password Incorrect. Please Verify Login")
        
    
    def listDataSets(self):
        print("Getting available Datasets")
        search_term = f"{self.endpoint}/datasets"
        request = requests.get(search_term,auth=HTTPBasicAuth(self.username,self.password))
        return request.json()
    
    def sampleDataSet(self, dataset, limit=None):
        if limit == None:
            limit = 25
        search_term = f"{self.endpoint}/datasets/internal/{dataset}/sample?limit={str(limit)}"
        request = requests.get(search_term,auth=HTTPBasicAuth(self.username,self.password))
        if request.status_code != 200:
            raise Exception(f"Status Code: {request.status_code}. Could not retrieve Data. Please check Parameters")
        df_sample = pd.DataFrame(request.json()['sample'])
        return df_sample
    
    def getDataSet(self, dataset, startTime, endTime):
        pattern = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
        if pattern.match(startTime) and pattern.match(endTime):
            start = f"{startTime[0:10]}T{startTime[11:13]}%3A{startTime[14:16]}%3A{startTime[17:19]}Z"
            end = f"{endTime[0:10]}T{endTime[11:13]}%3A{endTime[14:16]}%3A{endTime[17:19]}Z"
        else:
            raise Exception("Invalid Date format. Must be in Zulu Time. Example: 2022-01-01T12:00:00Z")
        search_term = f"{self.endpoint}/datasets/internal/{dataset}/filter?startTime={start}&endTime={end}" 
        request = requests.get(search_term,auth=HTTPBasicAuth(self.username,self.password))
        if request.status_code != 200:
            raise Exception(f"Status Code: {request.status_code}. Could not retrieve Data. Please check Parameters")
        content_filter = request.content
        content_filter_str = "[" + content_filter.decode('utf-8').replace("}{", "},{") + "]"
        df_filter = pd.json_normalize(json.loads(content_filter_str))
        return df_filter
    
    def listFileSets(self, path = None):
        print("Getting available Filesets")
        if path == None:
            search_term = f"{self.endpoint}/filesets"
        else:
            search_term = f"{self.endpoint}/filesets/{path}/list"
        request = requests.get(search_term,auth=HTTPBasicAuth(self.username,self.password))
        print(request.status_code)
        return request.json()
    
    def getFileSets(self, filesetId, path):
        search_term = f"{self.endpoint}/filesets/{filesetId}/download?file={path}"
        request = requests.get(search_term,auth=HTTPBasicAuth(self.username,self.password))
        filename = path.rsplit("/", 1)[-1]
        open(filename, 'wb').write(request.content)
        print("Download Finished")