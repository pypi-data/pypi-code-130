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
        self.base_url = base_url + '/' + version + '/'
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
        r = requests.post(self.base_url + 'auth', data={'username': username, 'password': password}).json()['token']
        self.auth_token = r.json()['token']
        self.token_type = r.json()['token_type']
        self.auth_header = {'Authorization': self.token_type + ' ' + self.auth_token}
        self.username = username
        self.session.headers.update(self.auth_header)

    def create_tracker(self, tracker: dict):
        """
        CreateTracker - Create a tracker
        """
        return self.post('/trackers', tracker)
    
    def get_tracker(self, tracker_id: str):
        """
        GetTracker - Get a tracker
        """
        return self.get('/trackers?tracker_id=' + tracker_id)
    
    def get_trackers(self, username: str = None):
        """
        GetTrackers - Get all trackers
        """
        if username:
            return self.get('/trackers/user?username=' + username)
        return self.get('/trackers/user')
    
    def update_tracker(self, tracker: dict):
        """
        UpdateTracker - Update a tracker
        """
        return self.put(f'/trackers/', tracker)
    
    def delete_tracker(self, tracker_id: str):
        """
        DeleteTracker - Delete a tracker
        """
        return self.delete(f'/trackers/{tracker_id}')
    
    def add_document(self, document: dict):
        """
        AddDocument - Add a document to a tracker
        """
        return self.post(f'/trackers/documents', document)
    
    def get_document(self, document_id: str):
        """
        GetDocument - Get a document
        """
        return self.get('/documents?document_id=' + document_id)
    
    def update_document(self, document: dict):
        """
        UpdateDocument - Update a document
        """
        return self.put(f'/documents/', document)
    
    def delete_document(self, document_id: str):
        """
        DeleteDocument - Delete a document
        """
        return self.delete('/documents?document_id=' + document_id)

    def link_document(self, tracker_id: str, document_id: str):
        """
        LinkDocument - Link a document to a tracker
        """
        return self.post(f'/trackers/{tracker_id}/documents', {'document_id': document_id})

    def get(self, url):
        """
        Get - Get data from Falcon API
        """
        return requests.get(self.base_url + url)

    def post(self, url, data):
        """
        Post - Post data to Falcon API
        """
        return requests.post(self.base_url + url, data)

    def put(self, url, data):
        """
        Put - Put data to Falcon API
        """
        return requests.put(self.base_url + url, data)

    def delete(self, url):
        """
        Delete - Delete data from Falcon API
        """
        return requests.delete(self.base_url + url)

    def patch(self, url, data):
        """
        Patch - Patch data to Falcon API
        """
        return requests.patch(self.base_url + url, data)

    def options(self, url):
        """
        Options - Get options from Falcon API
        """
        return requests.options(self.base_url + url)

    def head(self, url):
        """
        Head - Get head from Falcon API
        """
        return requests.head(self.base_url + url)

    def trace(self, url):
        """
        Trace - Get trace from Falcon API
        """
        return requests.trace(self.base_url + url)

    def connect(self, url):
        """
        Connect - Get connect from Falcon API
        """
        return requests.connect(self.base_url + url)

    def patch(self, url, data):
        """
        Patch - Patch data to Falcon API
        """
        return requests.patch(self.base_url + url, data)

    def options(self, url):
        """
        Options - Get options from Falcon API
        """
        return requests.options(self.base_url + url)
