import datetime
import asyncio
import io
import json
from json.decoder import JSONDecodeError
from urllib.parse import urlparse
from dataplate.client import DataPlate
# import os
# from pathlib import Path
# from urllib.parse import urlparse

import boto3
import botocore.exceptions

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado


def convert_times(o):
    if isinstance(o, datetime.datetime) or isinstance(o, datetime.timedelta):
        return o.__str__()
    else:
        raise TypeError("Object of type {} is not JSON serializable".format(type(o)))

class BaseHandler(APIHandler):
    """
    Top-level parent class.
    """

    session = boto3.session.Session()

    @property
    def scheduler(self):
        return self.settings["dataplate-lab"]

    def check_json(self):
        """Check to see if the incoming POST data is in JSON encoded format, cause that's all we understand.

        If it is in another format, write a 400 back to the client and return False, indicating that the
        handler method should return immediately. Otherwise, return True.
        """
        if self.request.headers["Content-Type"] != "application/json":
            self.set_status(
                400,
                "Bad Content-Type header: value: '{}'".format(
                    self.request.headers["Content-Type"]
                ),
            )
            self.set_header("Content-Type", "text/plain")
            self.finish("This server only accepts POST requests in 'application/json'")
            return False
        else:
            return True

    def required_params(self, params, required):
        """Check the incoming POST parameters to make sure that all the required parameters are included.

        Args:
          params (dict): The dictionary of params that was POSTed.
          required (list): A list of parameters that must be present in the params

        Returns:
          True, if all the required parameters are present and processing can continue.
          False, if there are missing paramters. Processing should return right away, the HTTP response is written already
        """
        for param in required:
            if param not in params:
                self.set_status(400, "Missing parameter: '{}'".format(param))
                self.set_header("Content-Type", "text/plain")
                self.finish(
                    "The parameter '{}' must be supplied with this POST request".format(
                        param
                    )
                )
                return False
        return True

    def load_params(self, required):
        """Loads the parameters to the POST request, checking for errors.
        The request must have the Content-Type 'application/json', be a well-formatted JSON object, and
        contain all the keys included in the required list.

        Args:
          required (list): The list of keys that must be inluded in the input for it to be valid.

        Returns:
          A dict object with the POSTed parameters if the are valid and None otherwise. If None is returned, processings
          the request should stop, the HTTP response has already been written.
        """
        if not self.check_json():
            return None

        try:
            data = json.loads(self.request.body.decode("utf-8"))

            if not self.required_params(data, ["image", "input_path", "notebook"]):
                return None
            else:
                return data
        except JSONDecodeError as e:
            self.set_status(400, "Improperly formatted JSON POST data")
            self.set_header("Content-Type", "text/plain")
            self.finish("JSON parser error: '{}'".format(str(e)))
            return False

    def json_response(self, response):
        """Take an object and return it to the client as a JSON formatted response"""
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(response, default=convert_times))

    def error_response(self, http_status, type, message):
        """Construct a JSON bad request error and return it to the client"""
        self.set_header("Content-Type", "application/json")
        self.set_status(http_status)
        self.finish(json.dumps(dict(error=dict(type=type, message=message))))

    def client_error_response(self, client_error):
        """Construct the error response when we get a boto ClientError"""
        http_status = client_error.response.get("HTTPStatusCode", 400)
        message = client_error.response.get("Error", {}).get("Message", "Unknown error")
        self.error_response(http_status, "ClientError", message)

    def botocore_error_response(self, core_error):
        """Construct the error response when we get a boto CoreError"""
        http_status = 400
        message = str(core_error)
        self.error_response(http_status, "BotoCoreError", message)

class DatasetsHandler(BaseHandler):

    @tornado.web.authenticated
    async def post(self):
        """
        Handler for listing the notebook runs.
        """
        try:
            # await self.tracker.update()
            data = json.loads(self.request.body.decode("utf-8"))
            self.log.debug(f'runs data: {data}')
            if data is None:
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            # self._serverURL = data.get("serverURL", "")
            # self._accessKey = data.get("accessKey", "")
            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            # if not self._serverURL or not self._accessKey or self._serverURL == "" or self._accessKey == "":
            #     self.error_response(404, "ServerError",
            #                         "DataPlate Configuration is invalid, please set your Server URL and Access Key")
            #     return
            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            datasets = []
            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            generator = dataplate.list_datasets()
            for dataset in json.loads(generator.reset_index().to_json(orient='records')):
                # self.log.debug(f'Described run job: {run["name"]}')
                await asyncio.sleep(0)
                datasets.append(dataset)

            self.json_response({"datasets": datasets})
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))


class RunsHandler(BaseHandler):
    # _tracker = None
    # _serverURL = ""
    # _accessKey = ""

    # @classmethod
    # def setTracker(cls, tracker):
    #     cls._tracker = tracker

    # @property
    # def tracker(self):
    #     if self._tracker is None:
    #         dataplate = DataPlate(access_key=self._accessKey, dataplate_uri=self._serverURL)
    #         self.setTracker(run.NotebookRunTracker(session=self.session, log=self.log))
    #     return self._tracker

    # @tornado.web.authenticated
    # async def get(self):
    #     """
    #     Handler for listing the notebook runs.
    #     """
    #     try:
    #         await self.tracker.update()
    #         runs = list(self.tracker)
    #         self.json_response({"runs": runs})
    #     except botocore.exceptions.ClientError as e:
    #         self.client_error_response(e)
    #     except botocore.exceptions.BotoCoreError as e:
    #         self.botocore_error_response(e)

    @tornado.web.authenticated
    async def post(self):
        """
        Handler for listing the notebook runs.
        """
        try:
            # await self.tracker.update()
            data = json.loads(self.request.body.decode("utf-8"))
            self.log.debug(f'runs data: {data}')
            if data is None:
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            # self._serverURL = data.get("serverURL", "")
            # self._accessKey = data.get("accessKey", "")
            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            # if not self._serverURL or not self._accessKey or self._serverURL == "" or self._accessKey == "":
            #     self.error_response(404, "ServerError",
            #                         "DataPlate Configuration is invalid, please set your Server URL and Access Key")
            #     return
            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            runs = []
            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            generator = dataplate.list_runs_notebook(n=20)
            for run in json.loads(generator.reset_index().to_json(orient='records')):
                # self.log.debug(f'Described run job: {run["name"]}')
                await asyncio.sleep(0)
                runs.append(run)

            self.json_response({"runs": runs})
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))


class RunHandler(BaseHandler):
    # @tornado.web.authenticated
    # def get(self, job_name):
    #     try:
    #         desc = run.describe_run(job_name, session=self.session)
    #         self.json_response({"run": desc})
    #     except botocore.exceptions.ClientError as e:
    #         self.client_error_response(e)
    #     except botocore.exceptions.BotoCoreError as e:
    #         self.botocore_error_response(e)

    @tornado.web.authenticated
    def post(self, job_name):
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            if data is None:
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            desc = dataplate.describe_notebook_run(job_name)
            self.json_response({"run": desc})
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))

    @tornado.web.authenticated
    def delete(self, job_name):
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            if data is None:
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            dataplate.stop_run_notebook(job_name)
            self.finish()
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))


class OutputHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, job_name):
        try:
            # d = run.describe_run(job_name, session=self.session)
            #
            # s3obj = d["Result"]
            # o = urlparse(s3obj)
            # bucket = o.netloc
            # key = o.path[1:]
            #
            # s3 = self.session.resource("s3")
            # obj = s3.Object(bucket, key)  # pylint: disable=no-member
            # data = obj.get()["Body"].read().decode("utf-8")
            dataplate = DataPlate()
            d = dataplate.describe_notebook_run(job_name)
            s3obj = d["Result"]
            o = urlparse(s3obj)
            bucket = o.netloc
            key = o.path[1:]
            dataplate.download_notebook_result(job_name)

            data = None
            with open(key.rstrip("/"), 'r', encoding='utf-8') as f:
                data = f.read()

            if data:
                # response = dict(notebook=d["Notebook"], output_object=s3obj, data=data)
                response = dict(notebook=key, output_object=s3obj, data=data)
                self.json_response(response)
            else:
                self.error_response(500, "ServerError", str("couldn't parse output"))
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))

    @tornado.web.authenticated
    def post(self, job_name):
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            # data = self.load_params(["image", "input_path", "notebook"])
            if data is None:
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            d = dataplate.describe_notebook_run(job_name)
            if "Result" in d:
                s3obj = d["Result"]
                o = urlparse(s3obj)
                bucket = o.netloc
                key = o.path[1:]
                dataplate.download_notebook_result(s3obj)

                data = None
                keyHirarcy = key.split("/")
                if keyHirarcy and len(keyHirarcy)>0:
                    with open(keyHirarcy[-1], 'r', encoding='utf-8') as f:
                        data = f.read()

                    if data:
                        # response = dict(notebook=d["Notebook"], output_object=s3obj, data=data)
                        response = dict(notebook=d["Notebook"], output_object=s3obj, data=data)
                        self.json_response(response)
                    else:
                        self.error_response(500, "ServerError", str("couldn't parse output"))
                else:
                    self.error_response(500, "ServerError", str("couldn't parse output"))
            else:
                self.error_response(500, "ServerError", str(f"No Result in description of Job {job_name}"))
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))


class RulesHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        """Handler for listing the schedules"""
        try:
            self.log.debug('inside rules handler')
            schedules = []
            dataplate = DataPlate()
            generator = dataplate.list_schedules_notebook(n=20)
            for schedule in json.loads(generator.reset_index().to_json(orient='records')):
                self.log.debug(f'Described rule: {schedule["name"]}')
                await asyncio.sleep(0)
                schedules.append(schedule)
            self.json_response({"schedules": schedules})
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))

    @tornado.web.authenticated
    async def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        # data = self.load_params(["image", "input_path", "notebook"])
        if data is None:
            self.error_response(404, "ServerError", "DataPlate Configuration is invalid, please set your Server URL and Access Key")
            return

        try:
            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            schedules = []
            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            generator = dataplate.list_schedules_notebook(n=20)
            for schedule in json.loads(generator.reset_index().to_json(orient='records')):
                self.log.debug(f'Described rule: {schedule["name"]}')
                await asyncio.sleep(0)
                schedules.append(schedule)
            self.json_response({"schedules": schedules})
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))


class RuleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, rule_name):
        """Get information on a specific schedule"""
        try:
            dataplate = DataPlate()
            schedule = dataplate.list_schedules_notebook(rule_prefix=rule_name)
            self.json_response({"schedules": [schedule]})
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))

    @tornado.web.authenticated
    def post(self, rule_name):
        # data = self.load_params(["image", "input_path", "notebook", "serverURL", "accessKey"])
        # if data is None:
        #     return
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            if data is None:
                return

            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            params = data.get("parameters", {})
            if isinstance(params, str):
                params = json.loads(params)

            kwargs = dict(
                rule_name=rule_name,
                image=data["image"],
                # input_path=data["input_path"],
                # output_prefix=data.get("output_prefix", None),
                notebook_file_path=data["input_path"],
                parameters=params,
                role=data.get("role", None),
                schedule=data.get("schedule", None),
                event_pattern=data.get("event_pattern", None),
            )
            instance_type = data.get("instance_type", None)
            if instance_type:
                kwargs["instance_type"] = instance_type
            securityGroupIds = data.get("securityGroupIds", None)
            if securityGroupIds:
                kwargs["securityGroupIds"] = securityGroupIds.split(",")
            subnets = data.get("subnets", None)
            if subnets:
                kwargs["subnets"] = subnets.split(",")

            max_time_limit_minutes = data.get("max_time_limit_minutes", 120)
            if max_time_limit_minutes:
                kwargs["max_time_limit_minutes"] = int(data.get("max_time_limit_minutes", 120))

            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            dataplate.schedule_notebook(**kwargs)
            self.json_response(dict(rule_name=rule_name))
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))

    @tornado.web.authenticated
    def delete(self, rule_name):
        """Delete a rule"""
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            if data is None:
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            dataplate.stop_schedule_notebook(rule_name=rule_name)
            self.finish()
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))


class InvokeHandler(BaseHandler):
    def post(self):
        try:
            # data = self.load_params(["image", "input_path", "notebook", "serverURL", "accessKey"])
            data = json.loads(self.request.body.decode("utf-8"))
            if data is None:
                return
            # self.log.debug(f'invoke now data: {data}')

            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            schedules = []
            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)

            # data = self.load_params(["image", "input_path", "notebook"])
            # if data is None:
            #     return

            params = data.get("parameters", {})
            if isinstance(params, str):
                params = json.loads(params)

            kwargs = dict(
                image=data.get("image", None),
                notebook_file_path=data["input_path"],
                # output_prefix=data.get("output_prefix", None),
                # notebook=data["notebook"],
                parameters=params,
                role=data.get("role", None)
            )
            instance_type = data.get("instance_type", None)
            if instance_type:
                kwargs["instance_type"] = instance_type
            securityGroupIds = data.get("securityGroupIds", None)
            if securityGroupIds:
                kwargs["securityGroupIds"] = securityGroupIds.split(",")
            subnets = data.get("subnets", None)
            if subnets:
                kwargs["subnets"] = subnets.split(",")

            max_time_limit_minutes = data.get("max_time_limit_minutes", 120)
            if max_time_limit_minutes:
                kwargs["max_time_limit_minutes"]=int(data.get("max_time_limit_minutes", 120))

            job_name = dataplate.run_notebook(**kwargs)
            self.json_response(dict(job_name=job_name))
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except ValueError as ve:
            self.error_response(400, "ValueError", str(ve))
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))


class ProjectsHandler(BaseHandler):

    @tornado.web.authenticated
    async def post(self):
        """
        Handler for listing the notebook runs.
        """
        try:
            # await self.tracker.update()
            data = json.loads(self.request.body.decode("utf-8"))
            self.log.debug(f'runs data: {data}')
            if data is None:
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            # self._serverURL = data.get("serverURL", "")
            # self._accessKey = data.get("accessKey", "")
            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            # if not self._serverURL or not self._accessKey or self._serverURL == "" or self._accessKey == "":
            #     self.error_response(404, "ServerError",
            #                         "DataPlate Configuration is invalid, please set your Server URL and Access Key")
            #     return
            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            projects = []
            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            generator = dataplate.list_projects(n=100)
            for project in json.loads(generator.reset_index().to_json(orient='records')):
                # self.log.debug(f'Described run job: {run["name"]}')
                await asyncio.sleep(0)
                projects.append(project)

            self.json_response({"projects": projects})
        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))



class SubProjectsHandler(BaseHandler):

    @tornado.web.authenticated
    async def post(self, project_name):
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            if data is None:
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            serverURL = data.get("serverURL", "")
            accessKey = data.get("accessKey", "")

            if not serverURL or not accessKey or serverURL == "" or accessKey == "":
                self.error_response(404, "ServerError",
                                    "DataPlate Configuration is invalid, please set your Server URL and Access Key")
                return

            subprojects = []
            dataplate = DataPlate(access_key=accessKey, dataplate_uri=serverURL)
            generator = dataplate.list_sub_projects(project_name=project_name,n=50)
            for subproject in json.loads(generator.reset_index().to_json(orient='records')):
                # self.log.debug(f'Described run job: {run["name"]}')
                await asyncio.sleep(0)
                subprojects.append(subproject)

            self.json_response({"projects": subprojects})

        except botocore.exceptions.ClientError as e:
            self.client_error_response(e)
        except botocore.exceptions.BotoCoreError as e:
            self.botocore_error_response(e)
        except Exception as ex:
            self.error_response(500, "ServerError", str(ex))
        except SystemExit as se:
            self.error_response(500, "ServerError", str(se))



class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": "This is /dataplate-lab/get_example endpoint!"
        }))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    prefix = "dataplate-lab"
    route_pattern = url_path_join(base_url, prefix, "get_example")
    schedule_pattern = url_path_join(base_url, prefix, "schedules")
    schedule_details_pattern = url_path_join(base_url, prefix, "schedule/(.+)")
    run_details_pattern = url_path_join(base_url, prefix, "run/(.+)")
    runs_pattern = url_path_join(base_url, prefix, "runs")
    output_pattern = url_path_join(base_url, prefix, "output/(.+)")
    invoke_pattern = url_path_join(base_url, prefix, "run")
    datasets_pattern = url_path_join(base_url, prefix, "datasets")
    projects_pattern = url_path_join(base_url, prefix, "projects")
    subprojects_pattern = url_path_join(base_url, prefix, "subprojects/(.+)")
    handlers = [(route_pattern, RouteHandler), (schedule_pattern, RulesHandler),(schedule_details_pattern,RuleHandler),
                (run_details_pattern,RunHandler),(runs_pattern,RunsHandler),(output_pattern,OutputHandler),(invoke_pattern,InvokeHandler),
                (datasets_pattern,DatasetsHandler),(projects_pattern,ProjectsHandler),(subprojects_pattern,SubProjectsHandler)]

    # prefix = "/dataplate-lab/"
    # handlers = [
    #     ("runs", RouteHandler),
    #     # ("run/(.+)", RunHandler),
    #     # ("run", InvokeHandler),
    #     # ("schedules", RulesHandler),
    #     # ("schedule/(.+)", RuleHandler),
    #     # ("upload", UploadHandler),
    #     # ("output/(.+)", OutputHandler),
    # ]

    web_app.add_handlers(host_pattern, handlers)
