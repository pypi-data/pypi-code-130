import json
import regex as re
import requests as rq
from constants import DBREPO_TEST_INSTANCE
from error import InvalidIdentifier
from query import Query
import pandas as pd


class Container:
    
    def __init__(self, **kwargs) -> None:
        self.dict = kwargs
        self.fetch_meta()

    def fetch_meta(self):
        url = f'{self.endpoint}/container'
        res = rq.get(url, verify=False)




class Client:

    def __init__(self, username : str = None, password : str = None, url : str = DBREPO_TEST_INSTANCE) -> None:
        print(username, password)
        self.url = url
        self.endpoint = f'{self.url}/api'
        self.__auth(username, password)
        # self.fetch_meta()


    def __auth(self, username : str, password : str) -> None:

        url = f'{self.endpoint}/auth'
        json = { 'username' : username, 'password' : password }

        res = rq.post(url, json=json, verify=False)
        json = res.json()
        self.token = self.__validate_auth_res(json)
        self.token = 'Bearer ' + self.token


    def __validate_auth_res(self, res: dict) -> str:

        if 'error' in res or 'token' not in res:
            if res['status'] == 401:
                raise ValueError('Authentication failed - username or password are wrong')
            else:
                raise ValueError('Authentication failed')

        return res['token']

    def fetch_meta(self):

        url = f'{self.endpoint}/container'
        res = rq.get(url, verify=False)
        self.container = { c['id'] : Container(**c) for c in res.json()}
        {}

        # print(pd.DataFrame(res.json()))

    def query_by_pid(self, pid) -> Query:

        if isinstance(pid,str) and not pid.isnumeric():
            result = re.search('.*/pid/(.*)', pid)
            if result == None:
                raise InvalidIdentifier(
                    f"Could not resolve pid '{pid}'. Please provide a correct pid like '{self.url}/pid/12345' or '12345'"
                    )
            pid = result.group(1)

        url = f'{self.endpoint}/pid/{pid}'

        res = rq.get(url, headers=self.__header(), verify=False)
        data = res.json()

        return self.query(data['cid'], data['dbid'], data['qid'])


    def query(self, cid: int, dbid: int, qid: int) -> Query:

        url = f'{self.endpoint}/container/{cid}/database/{dbid}/query/{qid}'

        res = rq.put(url, headers=self.__header(), verify=False)
        data = res.json()
        df = pd.DataFrame(data['result'])
        
        return df

    def query_by_statement(self, cid: int, dbid: int, statement : str) -> Query:

        url = f'{self.endpoint}/container/{cid}/database/{dbid}/query'
        json = {'statement' : statement}
        
        res = rq.put(url, headers=self.__header(), json=json, verify=False)
        data = res.json()
        df = pd.DataFrame(data['result'])

        return df

    def __header(self):
        return {'Authorization': self.token}


# client = Client(username='jtaha', password='fair12345')
# client.query_by_pid('https://dbrepo.ossdip.at/pid/4')




# client.query(1,1,21)
# client.query_by_statement(1,1,"SELECT `start` FROM `ubahnen_wien`")

# TODO: overview over all Databases