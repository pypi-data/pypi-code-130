import re
from inspect import signature
from typing import Any

from awslambdaric.lambda_context import LambdaContext
from pydantic import BaseModel, create_model

from pydantic_lambda_handler.main import PydanticLambdaHandler
from pydantic_lambda_handler.middleware import BaseHook


class APIGenerationHook(BaseHook):
    """Gen open api"""

    title: str
    version: str
    paths: dict[str, Any] = {}

    @classmethod
    def method_init(cls, **kwargs):
        app: PydanticLambdaHandler = kwargs["self"]
        status_code = kwargs["status_code"]
        open_api_status_code = str(int(status_code))
        method = kwargs["method"]
        APIGenerationHook.title = app.title
        APIGenerationHook.version = app.version

        url = kwargs["url"]
        if url in cls.paths:
            cls.paths[url].update(
                {
                    method: {
                        "responses": {
                            open_api_status_code: {
                                "description": kwargs["description"],
                                "content": {"application/json": {}},
                            }
                        },
                    }
                }
            )
        else:
            cls.paths[url] = {
                method: {
                    "responses": {
                        open_api_status_code: {
                            "description": kwargs["description"],
                            "content": {"application/json": {}},
                        }
                    },
                }
            }

        if kwargs["operation_id"]:
            cls.paths[url][method]["operationId"] = kwargs["operation_id"]

    @classmethod
    def pre_path(cls, **kwargs) -> None:
        sig = signature(kwargs["func"])

        if sig.parameters:

            url = kwargs["url"]
            method = kwargs["method"]

            path_model_dict = {}
            query_model_dict = {}

            body_model = None

            path_parameters_list = list(re.findall(r"\{(.*?)\}", url))
            path_parameters = set(path_parameters_list)

            if len(path_parameters_list) != len(path_parameters):
                raise ValueError(f"re-declared path variable: {url}")

            for param, param_info in sig.parameters.items():
                if param in path_parameters:
                    if param_info.annotation == param_info.empty:
                        annotations = str, ...
                    else:
                        annotations = param_info.annotation, ...
                else:
                    default = ... if param_info.default == param_info.empty else param_info.default
                    if param_info.annotation == param_info.empty:
                        annotations = str, default
                    else:
                        annotations = param_info.annotation, default

                if param in path_parameters:
                    if param_info.default != param_info.empty:
                        raise ValueError("Should not set default for path parameters")
                    path_model_dict[param] = annotations
                else:
                    model, body_default = annotations
                    if issubclass(model, BaseModel):
                        if body_model:
                            raise ValueError("Can only use one Pydantic model for body only")
                        body_model = model  # type: ignore
                        body_model._alias = param  # type: ignore
                    else:
                        query_model_dict[param] = annotations

            if path_parameters != set(path_model_dict.keys()):
                raise ValueError("Missing path parameters")

            APIPathModel = create_model("APIPathModel", **path_model_dict, **query_model_dict)  # type: ignore

            path_schema_initial = APIPathModel.schema()
            properties = []
            for name, property_info in path_schema_initial.get("properties", {}).items():
                #  {"name": "petId", "in": "path", "required": True, "schema": {"type": "string"}}
                in_ = "path" if name in path_parameters else "query"
                p = {"name": name, "in": in_, "schema": {"type": property_info.get("type", "string")}}
                if name in path_schema_initial.get("required", ()):
                    p["required"] = True

                properties.append(p)

            cls.paths[url][method]["parameters"] = properties
            if body_model:
                cls.paths[url][method]["requestBody"] = {
                    "content": {"application/json": {"schema": body_model.schema()}}  # type: ignore
                }

    @classmethod
    def pre_func(cls, event, context) -> tuple[dict, LambdaContext]:
        return event, context

    @classmethod
    def post_func(cls, body) -> Any:
        return body

    @classmethod
    def generate(cls):
        return {
            "openapi": "3.0.2",
            "info": {"title": cls.title, "version": cls.version},
            "paths": cls.paths,
        }
