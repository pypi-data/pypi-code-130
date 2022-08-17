import datetime
import json
import os
import subprocess
import traceback

import coolname

from deque.rest_connect import RestConnect
from deque.deque_environment import AGENT_API_SERVICE_URL
from deque.redis_services import RedisServices
import pickle
import multiprocessing
from deque.parsing_service import ParsingService
from deque.datatypes import Image, Audio, Histogram, BoundingBox2D
from deque.util import MODEL, CODE, DATA, ENVIRONMENT, RESOURCES
import requests
import glob

'''
def decode_datetime(obj):
    if '__datetime__' in obj:
        obj = datetime.datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
    return obj


def encode_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
    return obj
'''
'''
def _start_transport_service():
    try:
        print("Starting transport")
        import redis_server
        bin_path = str(redis_server.REDIS_SERVER_PATH)
        subprocess.run([bin_path])
        print("started successfully")
    except Exception as e:
        print(e)
        traceback.print_exc()

#_start_transport_service()
'''


class Run:

    # _submission_count = 1
    def __init__(self):
        self.user_name = None

        self._workload_type = None
        # self._submission_id = None

        self.project_id = None
        self._project_name = None

        self.params = dict()
        self._history = dict()
        self._step = 1
        self._run_id = None
        self._rest = RestConnect()

        self.run_meta_data = None
        self._model_logged = False

        self._code_logged = False

        self._environment_logged = False

        self._resources_logged = False

    def init(self, user_name=None, project_name=None, api_key=None):
        self.user_name = user_name

        self._api_key = api_key

        autenticated = self._authenticate()
        if not autenticated:
            raise ValueError("Invalid user and/or api key")

        self._workload_type = os.getenv("workload_type")
        self._workload_id = os.getenv("workload_id")
        self._submission_id = os.getenv("submission_id")

        if project_name is None:
            if self._workload_id is None:
                raise ValueError("Project name cannot be empty")
            else:
                self._project_name = self._workload_id
        else:
            self._project_name = project_name
        self._run_id = str(coolname.generate_slug(2))
        self._step = 1

        p2 = multiprocessing.Process(target=self._start_parser)
        p2.start()
        self._redis.flushall()
        self._redis.sadd("run_ids:", self._run_id)

        self._run_meta_data = {"submission_id": self._submission_id, "run_id": self._run_id,
                               "workload_type": self._workload_type, "workload_id": self._workload_id,
                               "project_name": self._project_name, "user_name": user_name}

        print("Run initialized with run id: " + self._run_id)

    '''
    def _generate_submission_id(self):
        req_data = {"submission_id":self._submission_id,"user_name":self.user_name,"workload_type":self._workload_type,"workload_id":self._workload_id}
        resp = self._rest.post(AGENT_API_SERVICE_URL+"/fex/submission/exists/",json=req_data)
        resp_data = resp.json()
        if resp_data["exists"]==True:
            self._submission_id = str(coolname.generate_slug(2))

            self._version_code()
            req_data = {"submission_id": self._submission_id, "user_name": self.user_name,
                        "workload_type": self._workload_type, "workload_id": self._workload_id,"parent_submission_id":self._parent_submission_id}
            resp = self._rest.post(AGENT_API_SERVICE_URL + "/fex/submission/create/", json=req_data)
            Run._submission_count+=1




    def _version_code(self):

        # by updating the submission_id in the environment variable, the agent will not autosave to the new submission
        full_env_var = "notebook_submission_details"
        current_submissions_str = os.getenv(full_env_var)
        if current_submissions_str is not None:

            current_submissions = json.loads(current_submissions_str)

            for submission in current_submissions:
                if self._workload_id == submission['notebook_id']:
                    submission.update({"submission_id":self._submission_id})
                    break

            os.environ[full_env_var] = json.dumps(current_submissions)
        else:
            print("Auto-Versioning failed. Please press Command-S")


    '''

    def _start_parser(self):
        parser = ParsingService()
        parser.receive()

    def _send_data_to_redis(self, step, data):

        key = "run_id:step:data:" + self._run_id + str(step)

        self._redis.sadd("run_id:steps:" + self._run_id, str(step))

        data_pickled = pickle.dumps(data)

        self._redis.set(key, data_pickled)

    def log(self, data, step=None, commit=True):
        # self._validate_data(data=data)
        full_data = {"experiment_data": data}
        full_data.update(
            {"user_name": self.user_name, "run_id": self._run_id, "workload_type": self._workload_type,
             "workload_id": self._workload_id, "submission_id": self._submission_id,
             "project_name": self._project_name, "deque_log_time": datetime.datetime.now(), "step": self._step})

        self.send_data_to_redis(step=self._step, data=full_data)
        if commit:
            self._step += 1

    def log_artifact(self, artifact_type, path):
        if self._run_meta_data is None:
            raise ValueError("Run not initialized. Please call init first")
        # s3://dequeapp-deque/users/riju@deque.app/projects/dex_audio/runs/adamant-galago/

        p2 = multiprocessing.Process(target=self._log_artifact_task, args=(artifact_type, path, self._run_meta_data))
        p2.start()

    def log_artifact_task(self, artifact_type, path, run_meta_data):
        self.user_name = "riju@deque.app"
        self._project_name = "dex_audio"
        self._run_id = "adamant-galago"
        print("I am saving artifact")
        file_name = os.path.basename(path)

        if artifact_type == MODEL:
            dest_path = "users/" + self.user_name + "/projects/" + self._project_name + "/runs/" + self._run_id + "/model/" + file_name
        elif artifact_type == CODE:
            dest_path = "users/" + self.user_name + "/projects/" + self._project_name + "/runs/" + self._run_id + "/code/" + file_name
        elif artifact_type == ENVIRONMENT:
            dest_path = "users/" + self.user_name + "/projects/" + self._project_name + "/runs/" + self._run_id + "/environment/" + file_name




        elif artifact_type == RESOURCES:
            dest_path = "users/" + self.user_name + "/projects/" + self._project_name + "/runs/" + self._run_id + "/resources/"
        else:
            raise ValueError(
                "artifact_type must be model (file), environment (file), code (file) or resources (directory)")

        print(AGENT_API_SERVICE_URL + "/fex/drive/contents/upload/presigned_url/read/")

        # Demonstrate how another Python program can use the presigned URL to upload a file
        if os.path.isdir(path):
            artifact_uris = []
            for filename in glob.iglob(path + '**/**', recursive=True):
                if os.path.isdir(filename):
                    continue
                dest_path = dest_path + filename
                req_data = {"user_name": self.user_name, "destination_path": dest_path}
                resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/drive/contents/upload/presigned_url/read/",
                                     json=req_data)
                res = resp.json()
                print(res)
                with open(filename, 'rb') as f:
                    files = {'file': (filename, f)}
                    if "fields" in res:
                        http_response = requests.post(url=res['url'], data=res['fields'], files=files)
                    else:
                        # TODO: for google we need a different way to save data
                        object_text = f.read()
                        headers = {'Content-type': "application/octet-stream"}
                        http_response = requests.put(url=res['url'], data=object_text, headers=headers)
                    print(http_response)
                # we record the meta data
            artifact_uris.append(dest_path)
            req_data = {"user_name": self.user_name, "destination_path": dest_path, "artifact_type": artifact_type,
                        "project_name": self._project_name, "run_id": self._run_id, "artifact_uris": artifact_uris}
            resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/artifact/metadata/create/",
                                 json=req_data)
            res = resp.json()
            print(res)

        else:
            req_data = {"user_name": self.user_name, "destination_path": dest_path}
            resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/drive/contents/upload/presigned_url/read/",
                                 json=req_data)
            res = resp.json()
            with open(path, 'rb') as f:
                files = {'file': (path, f)}
                if "fields" in res:
                    http_response = requests.post(url=res['url'], data=res['fields'], files=files)
                else:
                    # TODO: for google we need a different way to save data
                    object_text = f.read()
                    headers = {'Content-type': "application/octet-stream"}
                    http_response = requests.put(url=res['url'], data=object_text, headers=headers)
                print(http_response)
            req_data = {"user_name": self.user_name, "destination_path": dest_path, "artifact_type": artifact_type,
                        "project_name": self._project_name, "run_id": self._run_id, "artifact_uris": [dest_path]}
            resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/artifact/metadata/create/",
                                 json=req_data)
            res = resp.json()
            print(res)

        if artifact_type == MODEL:
            self._model_logged = True
        elif artifact_type == CODE:
            self._code_logged = True
        elif artifact_type == ENVIRONMENT:
            self._environment_logged = True
        elif artifact_type == RESOURCES:
            self._resources_logged = True
        # If successful, returns HTTP status code 204

    def register_artifacts(self, latest=True, label=None, tags=None):
        if not self._model_logged:
            raise ValueError(
                "Please log the model (and optionally code and environment) before calling register_artifacts")
        req_data = {"user_name": self.user_name, "latest": latest, "label": label,
                    "project_name": self._project_name, "run_id": self._run_id, "tags": tags}
        resp = requests.post(url=AGENT_API_SERVICE_URL + "/fex/project/artifacts/register/",
                             json=req_data)
        res = resp.json()
        print(res)

    def load_model(self, model, version="latest"):
        self.user_name = "riju@deque.app"
        self._project_name = "dex_audio"
        self._run_id = "adamant-galago"
        print("I am loading model artifact")

    def _validate_data(self, data):
        for key, value in data.items():
            if type(value) is dict:
                self._validate_data(value)
            else:
                # print(type(value))
                if type(value) in [Audio, BoundingBox2D, Histogram,
                                   Image] or value.__class__.__module__ == '__builtin__':
                    pass
                else:
                    raise ValueError(
                        "Invalid type in dictionary. Allowed values include builtin types and Deque data types " + str(
                            type(value)) + " " + str(value.__class__.__module__))

    def _send_upstream(self):
        self._rest.post(url=AGENT_API_SERVICE_URL + "/fex/python/track/", json=self._history)
        self._history = dict()

    def _authenticate(self):
        return True


if __name__ == "__main__":
    deque = Run()

    deque.log_artifact_task(artifact_type=RESOURCES, path="/home/riju/Documents/deque/dequeapp/dequeapp.egg-info",
                            run_meta_data=None)
    # deque.init(user_name="riju@deque.app", project_name="awesome-dude")
    # for i in range(100):
    # deque.log(data={"train": {"accuracy": i, "loss": i - 100}, "image": deque.im})

    # deque.log(data={"image":deque.im})
