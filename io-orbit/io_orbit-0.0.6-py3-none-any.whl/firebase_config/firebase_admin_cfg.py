import firebase_admin
from firebase_admin import storage
from firebase_admin import credentials
import gcsfs
import os
from io_orbit.logger.laccuna_logging import get_logger
logger = get_logger(__name__)

class FirebaseBucketRights():
    def __init__(self) -> None:
        self.filesystem = gcsfs.GCSFileSystem(project=os.getenv('IO_PROJECT'), token=eval(os.getenv('IO_KEY')))
        self.credentials = credentials.Certificate(eval(os.getenv('IO_KEY')))
        self.initialize_app = firebase_admin.initialize_app(self.credentials)
        pass

    def initialize_firebase(self):
        fs = self.filesystem
        cred = self.credentials
        self.initialize_app
        return fs

if not firebase_admin._apps:
    logger.info(f"Instantiating Firebase App...")
    fs = FirebaseBucketRights().initialize_firebase()
else:
    logger.warning(f"Firebase admin app already initialized: {firebase_admin._apps}")