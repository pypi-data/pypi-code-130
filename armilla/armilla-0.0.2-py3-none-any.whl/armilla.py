import requests
from copy import deepcopy

class Url:
    def __init__(self, url) -> None:
        self.__url = url

    def __str__(self):
        return self.__url

    def _repr_html_(self):
        """HTML link to this URL."""
        return f'<a href="{self.__url}">{self.__url}</a>'

class ArmillaClient:
    def __init__(self, username, password, env="PRODUCTION"):
        self.base_url, self.url = self._get_url_from_env(env)
        self.username = username
        self.password = password
        self.auth_token = self._get_auth_token(username, password)

    def _get_headers(self):
        return {
            "Authorization": self.auth_token
        }

    def _get_url_from_env(self, env):
        if env == "PRODUCTION":
            return ("https://app.hosted.armilla.ai/", "https://app.hosted.armilla.ai/backend/")
        elif env == "STAGING":
            return ("https://app.staging-aws.armilla.ai/", "https://app.staging-aws.armilla.ai/backend/")
        elif env == "DEMO":
            return ("https://app.demo.armilla.ai/", "https://app.demo.armilla.ai/backend/")
        elif env == "LOCAL":
            return ("http://127.0.0.1:3000/", "http://127.0.0.1:8000/")
        else:
            raise Exception("Not a valid env: (PRODUCTION, STAGING, DEMO, LOCAL")

    def run(self, run_name, model_id, test_plan_id, user_id, project_id):
        """
            Trigger an analysis run from a project's test plan + model

                Parameters:
                    run_name: name of test run shown on project
                    model_id: id of model in project
                    test_plan_id: id of project test plan to run
                    user_id: user id
                    project_id: project id
                Returns:
                    response: model object from response
        """
        request_url = self.url + "api/testPlanRuns/"
        headers = self._get_headers()
        request_body = {
            "modelDefinitionId": model_id,
            "name": run_name,
            "project": project_id,
            "testPlanId": test_plan_id,
            "userId": user_id
        }
        response = requests.post(request_url, data=request_body, headers=headers)

        if response.status_code != 200:
            raise Exception("Failed to trigger run")
        else:
            return_response = response.json()
            return self._build_test_run_url(project_id, return_response["id"])
    
    def upload_model(self, model_name, user_id, model_path, phase_id, runner_type, project_id, description=""):
        """
            upload a model from local file path to a project

                Parameters:
                    model_name: name of model shown on project
                    user_id: user id
                    model_path: local file path of the model file
                    phase_id: project phase id
                    runner_type: type of model runner
                    project_id: project id
                Returns:
                    response: model object from response
        """
        request_url = self.url + "api/modelDefinitions/"
        with open(model_path, 'rb') as f:
            request_body = {
                "modelName": model_name,
                "user": user_id,
                "phase": phase_id,
                "description": description,
                "runnerType": runner_type,
                "project": project_id,
                "modelLocationType": "FILE_SYSTEM"
            }
            file_body = {
                "file": f,
            }
            headers = self._get_headers()
            
            response = requests.post(request_url, files=file_body, data=request_body, headers=headers)
            return response.json()

    def upload_data_set(self, dataset_name, dataset_path, user_id, phase_id, project_id, description="", source_type="E"):
        """
            upload a dataset from local file path to a project

                Parameters:
                    dataset_name: name of dataset shown on project
                    dataset_path: local file path of the dataset file
                    user_id: user id
                    phase_id: project phase id
                    project_id: project id
                Returns:
                    response: dataset object from response
        """
        request_url = self.url + "api/datasets/"
        headers = self._get_headers()
        with open(dataset_path, 'rb') as f:
            file_body = {
                "file": f
            }
            request_body = {
                "sourceType": source_type,
                "creator": user_id,
                "datasetName": dataset_name,
                "datasetLocationType": "FILE_SYSTEM",
                "description": description,
                "project": project_id,
                "phase": phase_id
            }
            response = requests.post(request_url, files=file_body, data=request_body, headers=headers)
            return response.json()

    def get_projects(self):
        request_url = self.url + "api/projects/"
        headers = self._get_headers()
        response = requests.get(request_url, headers=headers).json()

        projects = []
        for result in response["results"]:
            projects.append({
                "id": result["id"],
                "name": result["name"],
                "description": result["description"]
            })

        return projects

    def get_runs_for_project(self, project_id):
        request_url = self.url + "api/testPlanRuns/"
        headers = self._get_headers()
        params = {
            "project": project_id
        }

        response = requests.get(request_url, headers=headers, params=params)
        if response.status_code != 200:
            return Exception("Failed to fetch runs")
        else:
            return_response = []
            for run in response.json()["results"]:
                run["run_url"] = str(self._build_test_run_url(run["project"], run["id"]))
                return_response.append(run)

        return return_response

    def get_models_for_project(self, project_id):
        request_url = self.url + "api/modelDefinitions/"
        headers = self._get_headers()
        params = {
            "project": project_id
        }

        response = requests.get(request_url, headers=headers, params=params).json()

        model_definitions = []
        for result in response["results"]:
            model_definitions.append({
                "id": result["id"],
                "name": result["name"],
                "description": result["description"],
                "runner_type": result["runner_type"],
                "prediction_type": result["prediction_type"]
            })

        return model_definitions

    def get_test_plans_for_project(self, project_id):
        request_url = self.url + "api/testPlans/"
        headers = self._get_headers()
        params = {
            "project": project_id
        }

        response = requests.get(request_url, headers=headers, params=params)
        return response.json()["results"]
    
    def get_test_plan(self, test_plan_id):
        request_url = self.url + "api/testPlans/" + str(test_plan_id) + "/"
        headers = self._get_headers()

        response = requests.get(request_url, headers=headers)
        return response.json()
    
    def get_dataset(self, dataset_id):
        request_url = self.url + "api/datasets/" + str(dataset_id) + "/"
        headers = self._get_headers()

        response = requests.get(request_url, headers=headers)
        return response.json()
    
    def attach_dataset_to_testplan(self, test_plan_id, dataset_id):
        '''
        Attach an uploaded dataset to existing configured test plan,
        Will mimic the test pipeline config of the first dataset,
        The dataset and test plan should belong in the same project

            Parameter:
                dataset_id: existing id of an uploaded dataset
                test_plan_id: existing id of test plan
        '''

        test_plan = self.get_test_plan(test_plan_id)
        request_url = self.url + "api/testPlans/" + str(test_plan_id) + "/"
        headers = self._get_headers()
        if "scenarios" in test_plan:
            for scenario in test_plan["scenarios"]:
                if scenario["data_source"] == dataset_id:
                    raise Exception("dataset already attached")
            
            if len(test_plan["scenarios"]) == 0:
                raise Exception("test plan require existing scenarios")
            
            first_scenario = test_plan["scenarios"][0]
            copied_scenario = deepcopy(first_scenario)

            if "DATA_DRIFT_DETECTION" in copied_scenario["test_pipelines"] or "CONCEPT_DRIFT_DETECTION" in copied_scenario["test_pipelines"]:
                copied_scenario = self._reconcile_reference_data(copied_scenario)
            copied_scenario["data_source"] = dataset_id
            copied_scenario.pop("id", None)
            print(copied_scenario)
            request_body = {
                "scenarios": [
                    copied_scenario
                ]
            }

            response = requests.put(request_url, json=request_body, headers=headers)
            return response.json()
        
        raise Exception("existing scenarios required for test plan")

    def _reconcile_reference_data(self, scenario):
        reference_set = None
        if len(scenario.get("DATA_DRIFT_DETECTION", {}).get("data_drift_detection_configuration", [])) > 0:
            if scenario["DATA_DRIFT_DETECTION"]["data_drift_detection_configuration"][0].get("is_reference", False):
                reference_set = self.get_dataset(scenario["data_source"])

                scenario["DATA_DRIFT_DETECTION"]["data_drift_detection_configuration"][0] = {
                    "is_reference": False,
                    "reference_data": reference_set["data_url"]
                }

        if len(scenario.get("CONCEPT_DRIFT_DETECTION", {}).get("concept_drift_detection_configuration", [])) > 0:
            if scenario["CONCEPT_DRIFT_DETECTION"]["concept_drift_detection_configuration"][0].get("is_reference", False):
                if reference_set is None:
                    reference_set = self.get_dataset(scenario["data_source"])
                
                scenario["CONCEPT_DRIFT_DETECTION"]["concept_drift_detection_configuration"][0] = {
                    "is_reference": False,
                    "reference_data": reference_set["data_url"]
                }
        return scenario
    
    def _get_auth_token(self, username, password):
        '''
        Authenticates user request and returns auth token if successful

            Parameters:
                username: user login
                password: user password
            Returns:
                token: bearer token for client requests
        '''
        request_url = self.url + "api/request_token/"
        params = {
            "username": username,
            "password": password
        }
        if username is None:
            raise Exception("username required")
        if password is None:
            raise Exception("password required")

        response = requests.post(request_url, data=params)
        if response.status_code == 403:
            raise Exception(response.json())
        if response.status_code != 200:
            raise Exception("error requesting token")

        token = response.json()["token_type"] + " " + response.json()["access_token"]
        return token
    
    def _build_test_run_url(self, project_id, run_id):
        url = "{base_url}{project_id}/runs/{run_id}?selectedBucket=Fingerprint&selectedPipeline=TEST_ANALYSIS_SUMMARY".format(
            base_url=self.base_url,
            project_id=str(project_id),
            run_id=str(run_id)
        )
        return Url(
            url=url
        )
