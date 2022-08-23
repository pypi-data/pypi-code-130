import json
import regex as re
import requests as rq
from dbrepo.constants import DBREPO_TEST_INSTANCE
from dbrepo.error import InvalidIdentifier
from dbrepo.query import Query
import pandas as pd


class Container:
    
    def __init__(self, **kwargs) -> None:
        self.dict = kwargs
        self.fetch_meta()

    def fetch_meta(self):
        url = f'{self.endpoint}/container'
        res = rq.get(url, verify=self.verifyTLS)




class Client:

    def __init__(self, username : str = None, password : str = None, url : str = DBREPO_TEST_INSTANCE, verifyTLS = True) -> None:
        self.url = url
        self.verifyTLS = verifyTLS
        self.endpoint = f'{self.url}/api'
        self.__auth(username, password)
        # self.fetch_meta()


    def __auth(self, username : str, password : str) -> None:

        url = f'{self.endpoint}/auth'
        json = { 'username' : username, 'password' : password }

        res = rq.post(url, json=json, verify=self.verifyTLS)
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

    # def fetch_meta(self):

    #     url = f'{self.endpoint}/container'
    #     res = rq.get(url, verify=self.verifyTLS)
    #     self.container = { c['id'] : Container(**c) for c in res.json()}
    #     {}

    #     # print(pd.DataFrame(res.json()))

    def fetch_table_info(self,cid,dbid):

        url = f'{self.endpoint}/container/{cid}/database/{dbid}/table'
        res = rq.get(url, headers=self.__header(), verify=self.verifyTLS)
        data = res.json()
        df = pd.DataFrame(data)

        return df

    def fetch_database_info(self):
        url = f'{self.endpoint}/container'
        res = rq.get(url, headers=self.__header(), verify=self.verifyTLS)
        data = res.json()
        df = pd.DataFrame(data)

        return df

    def generate_table_in_database(self, cid, dbid, name, desc, columns):

        url = f'{self.endpoint}/container/{cid}/database/{dbid}/table'
        body = {
            'name': name,
            'description': desc,
            'columns': columns
        }
        
        rq.post(url, headers=self.__header(), json=body, verify=self.verifyTLS)

    def generate_database(self, name, description, public=True, repository="mariadb", tag="10.5"):

        url = f'{self.endpoint}/container'
        body = {
            "name": name,
            "repository": repository,
            "tag": tag
        }
        res = rq.post(url, headers=self.__header(), json=body, verify=self.verifyTLS)
        cid = res.json()['id']

        url = f'{self.endpoint}/container/{cid}'
        body = {
            'action': "start"
        }
        rq.put(url, headers=self.__header(), json=body, verify=self.verifyTLS)

        url = f'{self.endpoint}/container/{cid}/database'
        body = {
            "name": name,
            "description": description,
            "is_public": public
        }
        rq.post(url, headers=self.__header(), json=body, verify=self.verifyTLS)

        return cid


    def query_by_pid(self, pid) -> Query:

        if isinstance(pid,str) and not pid.isnumeric():
            result = re.search('.*/pid/(.*)', pid)
            if result == None:
                raise InvalidIdentifier(
                    f"Could not resolve pid '{pid}'. Please provide a correct pid like '{self.url}/pid/12345' or '12345'"
                    )
            pid = result.group(1)

        url = f'{self.endpoint}/pid/{pid}'

        res = rq.get(url, headers=self.__header(), verify=self.verifyTLS)
        data = res.json()

        return self.query(data['cid'], data['dbid'], data['qid'])


    def query(self, cid: int, dbid: int, qid: int) -> Query:

        url = f'{self.endpoint}/container/{cid}/database/{dbid}/query/{qid}'

        res = rq.put(url, headers=self.__header(), verify=self.verifyTLS)
        data = res.json()
        df = pd.DataFrame(data['result'])
        
        return df

    def query_by_statement(self, cid: int, dbid: int, statement : str) -> Query:

        url = f'{self.endpoint}/container/{cid}/database/{dbid}/query'
        json = {'statement' : statement}
        
        res = rq.put(url, headers=self.__header(), json=json, verify=self.verifyTLS)
        data = res.json()
        df = pd.DataFrame(data['result'])

        return df

    def __header(self):
        return {'Authorization': self.token}


    def add_data_table(self, cid: int, dbid: int, tid: int, df: pd.DataFrame):

        url = f'{self.endpoint}/container/{cid}/database/{dbid}/table/{tid}/data'
        for index, row in df.iterrows():
            json = {'data': row.to_dict()}   
            res = rq.post(url, headers=self.__header(), json=json, verify=self.verifyTLS)
