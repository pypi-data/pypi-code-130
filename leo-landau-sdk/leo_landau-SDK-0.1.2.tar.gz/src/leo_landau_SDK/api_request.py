import requests

from .api_object import ApiObject
from .api_result import ApiResult

BASE_URL = "https://the-one-api.dev/v2"

V = False

class ApiRequest:

    def __init__(self, result_type, access_token):
        self.result_type = result_type
        # result_type should be an ApiObject type
        if not isinstance(result_type(), ApiObject):
            raise RuntimeError("result_type should be a subclass of ApiObject")
        self.access_token = access_token
        self.obj_id = None
        self.params = {}

    def get_result(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        # the endpoint is specified in the ApiObject class
        url = BASE_URL + self.result_type.get_endpoint(self.obj_id)
        response = requests.get(url, headers=headers, params=self.params)
        if V:
            print(response.url)

        # parse the response into an api_result object
        try:
            raw_json = response.json()
            api_result = ApiResult[self.result_type](**raw_json)
        except requests.exceptions.JSONDecodeError:
            raise RuntimeError(f"Unable to parse response json: {response.text}")

        if not api_result.success:
            raise RuntimeError(api_result.message)

        if V:
            print(vars(api_result))

        # serialize the objects in 'docs' to the expected type
        docs = []
        for obj in api_result.docs:
            # serialize to result_type
            docs.append(self.result_type(**obj))

        api_result.docs = docs

        return api_result

    def get_all(self):
        return self.get_result()

    def get(self, _id=None):
        self.obj_id = _id
        return self.get_result()

    def limit(self, limit_val):
        self.params["limit"] = limit_val

    def page(self, page_val):
        self.params["page"] = page_val

    def offset(self, offset_val):
        self.params["offset"] = offset_val

    def sort_by(self, field, asc_desc="asc"):
        # TODO validate the field to ensure it's in the class
        if asc_desc not in ["asc", "desc"]:
            raise ValueError("asc_desc must be one of asc, desc")
        self.params["sort"] = f"{field}:{asc_desc}"

    def filter(self, filter_str):
        # TODO validate the filter_str
        self.params[filter_str] = ""
