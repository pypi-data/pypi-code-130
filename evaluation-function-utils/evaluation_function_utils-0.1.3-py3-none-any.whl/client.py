from dotenv import load_dotenv
import os
import json
import boto3

from .errors import EvaluationException


class MissingCredentials(Exception):
    pass


class EvaluationFunctionNotFound(Exception):
    pass


class EvaluationFunctionException(Exception):
    pass


class EvaluationFunctionClient():
    """ 
    Client wrapped around the botocore.client.Lambda, for invoking 
    deployed evaluation functions. It should be initialised outside of the 
    evaluation_function.
    """

    def __init__(self, env_path=None):
        """ 
        Intialise client, with optional path to .env file containing credentials
        """

        # Initialise Credentials for the lambda client
        self.get_credentials(env_path)

        # Initialise lambda client
        self.client = boto3.client('lambda',
                                   aws_access_key_id=self.ID,
                                   aws_secret_access_key=self.KEY,
                                   region_name=self.REGION)

        # Test client credentials?

    def get_credentials(self, env_path):
        """ 
        Fetches credentials for the IAM User with the lambda:invokeFunction 
        permission
        In the containerised version of the function, these are already 
        present as environment variables, but in local testing these need 
        to be loaded from a .env file
        """
        load_dotenv(env_path)

        # Get credentials
        self.ID = os.getenv("INVOKER_ID", default=False)
        self.KEY = os.getenv("INVOKER_KEY", default=False)
        self.REGION = os.getenv("INVOKER_REGION", default=False)

        # Raise exception if some are missing
        if (not self.ID) or (not self.KEY) or (not self.REGION):
            raise MissingCredentials("Missing AWS credentials")

    def invoke(self, name: str, response, answer, params={}) -> dict:
        """
        Invoke deployed evaluation function by 'name', supplying the required 
        answer and response, and optional params. All three need to be 
        JSON-serializable.
        """

        body = {
            "response": response,
            "answer": answer,
            "params": params,
        }

        # Construct and serialise payload
        payload = json.dumps({
            "headers": {
                "command": "eval"
            },
            "body": body,
        })

        # Attempt to call function
        try:
            res = self.client.invoke(FunctionName=name,
                                     Payload=payload,
                                     InvocationType="RequestResponse",
                                     LogType="Tail")
        except self.client.exceptions.ResourceNotFoundException as e:
            raise EvaluationFunctionNotFound(f"{name} not found") from e

        # Raise error if the status code isn't 200
        if res['StatusCode'] != 200:
            raise EvaluationFunctionException(
                f"{name} returned StatusCode {res['StatusCode']}",
                raw_response=res)

        # Decode payload
        decoded_str = res['Payload'].read().decode("utf-8")

        # Parse payload
        try:
            decoded = json.loads(decoded_str)
        except ValueError:
            raise EvaluationException(
                f"Payload response from the {name} function could not be parsed.",
                raw_response=decoded)

        # If there was an error in evaluation, raise it as if the function
        # was run locally.
        if "error" in decoded:
            raise EvaluationException(**decoded['error'])

        if "result" in decoded:
            return decoded["result"]
        else:
            raise EvaluationException(
                f"The {name} Evaluation function, did not return an error or a result.",
                raw_response=decoded)
