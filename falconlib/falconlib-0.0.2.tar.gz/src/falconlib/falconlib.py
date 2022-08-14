"""
falconlib.py - Client side library for Falcon API
"""
from functools import wraps
import requests


class FalconLib:
    """
    FalconLib - Client side library for Falcon API
    """
    def __init__(self, base_url: str, version: str = 'v1_0') -> None:
        """
        FalconLib - Client side library for Falcon API
        """
        self.base_url = base_url + '/api/v' + version
        self.version = version
        self.auth_token = None
        self.token_type = None
        self.auth_header = None
        self.username = None
        self.session = requests.Session()
    
    def authorize(self, username: str, password: str) -> None:
        """
        Authorize - Authorize user to Falcon API
        """
        r = requests.post(self.base_url + '/users/token', data={'username': username, 'password': password})
        print("***", r)
        self.auth_token = r.json()['access_token']
        self.token_type = r.json()['token_type']
        self.auth_header = {'Authorization': self.token_type + ' ' + self.auth_token}
        self.username = username
        self.session.headers.update(self.auth_header)

    def create_tracker(self, tracker: dict):
        """
        CreateTracker - Create a tracker
        """
        return self.__post('/trackers', tracker)
    
    def get_tracker(self, tracker_id: str):
        """
        GetTracker - Get a tracker
        """
        return self.__get('/trackers?tracker_id=' + tracker_id)
    
    def get_trackers(self, username: str = None):
        """
        GetTrackers - Get all trackers
        """
        if username:
            return self.__get('/trackers/user?username=' + username)
        return self.__get('/trackers/user')
    
    def update_tracker(self, tracker: dict):
        """
        UpdateTracker - Update a tracker
        """
        tracker.pop('documents', None)
        return self.__put(f'/trackers/', tracker)
    
    def delete_tracker(self, tracker_id: str):
        """
        DeleteTracker - Delete a tracker
        """
        return self.__delete(f'/trackers/?tracker_id={tracker_id}')
    
    def add_document(self, document: dict):
        """
        AddDocument - Add a document to the database
        """
        return self.__post(f'/documents', document)

    def get_document(self, document_id: str):
        """
        GetDocument - Get a document
        """
        return self.__get('/documents?doc_id=' + document_id)
    
    def get_documents(self, tracker_id: str):
        """
        GetDocuments - Get all documents
        """
        return self.__get(f'/trackers/{tracker_id}/documents')
    
    def update_document(self, document: dict):
        """
        UpdateDocument - Update a document
        """
        return self.__put(f'/documents/', document)
    
    def delete_document(self, document_id: str):
        """
        DeleteDocument - Delete a document
        """
        return self.__delete('/documents?doc_id=' + document_id)

    def link_document(self, tracker_id: str, document_id: str):
        """
        LinkDocument - Link a document to a tracker
        """
        return self.__patch(f'/trackers/{tracker_id}/documents/link/{document_id}')
    
    def unlink_document(self, tracker_id: str, document_id: str):
        """
        UnlinkDocument - Unlink a document from a tracker
        """
        return self.__patch(f'/trackers/{tracker_id}/documents/unlink/{document_id}')

    def __get(self, url: str):
        """
        Get - Get data from Falcon API
        """
        return requests.get(self.base_url + url, headers=self.auth_header)

    def __post(self, url:str, data: dict):
        """
        Post - Post data to Falcon API
        """
        return requests.post(self.base_url + url, json=data, headers=self.auth_header)

    def __put(self, url: str, data: dict):
        """
        Put - Put data to Falcon API
        """
        return requests.put(self.base_url + url, json=data, headers=self.auth_header)

    def __delete(self, url: str):
        """
        Delete - Delete data from Falcon API
        """
        return requests.delete(self.base_url + url, headers=self.auth_header)

    def __patch(self, url: str, data=None):
        """
        Patch - Patch data to Falcon API
        """
        return requests.patch(self.base_url + url, data=data, headers=self.auth_header)

    def __options(self, url: str):
        """
        Options - Get options from Falcon API
        """
        return requests.options(self.base_url + url)

    def __head(self, url: str):
        """
        Head - Get head from Falcon API
        """
        return requests.head(self.base_url + url)

    def __trace(self, url):
        """
        Trace - Get trace from Falcon API
        """
        return requests.trace(self.base_url + url)

    def __connect(self, url: str):
        """
        Connect - Get connect from Falcon API
        """
        return requests.connect(self.base_url + url)

    def options(self, url):
        """
        Options - Get options from Falcon API
        """
        return requests.options(self.base_url + url)
