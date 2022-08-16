"""
https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway-tutorial.html#services-apigateway-tutorial-prereqs
"""
import subprocess
import sys
from pathlib import Path
from tempfile import mkdtemp

from aws_cdk import Stack
from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda
from constructs import Construct

from pydantic_lambda_handler.gen_open_api_inspect import gen_open_api_inspect


def build_requirements():
    requirements_dir = Path(mkdtemp())
    root = Path(__file__).parents[2]

    # https://aws.amazon.com/premiumsupport/knowledge-center/lambda-python-package-compatible/
    # pip install \
    #     --platform manylinux2014_x86_64 \
    #     --target=my-lambda-function \
    #     --implementation cp \
    #     --python 3.9 \
    #     --only-binary=:all: --upgrade \
    #     pandas
    subprocess.run(
        (
            f"{sys.executable}",
            "-m",
            "pip",
            "install",
            f"{root}",
            "--upgrade",
            "--target",
            requirements_dir.joinpath("python"),
            "--platform",
            "manylinux2014_x86_64",
            "--implementation",
            "cp",
            "--python",
            "3.9",
            "--only-binary=:all:",
        ),
        check=True,
    )

    return requirements_dir


class DemoAppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        policy_statement_1 = iam.PolicyStatement(
            actions=[
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
            ],
            effect=iam.Effect.ALLOW,
            resources=["*"],
        )

        policy_statement_2 = iam.PolicyStatement(
            actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
            effect=iam.Effect.ALLOW,
            resources=["*"],
        )

        document = iam.PolicyDocument(statements=[policy_statement_1, policy_statement_2])

        iam.Policy(
            self,
            "id_123",
            policy_name="lambda-apigateway-policy",
            document=document,
        )

        user = iam.User(self, "myuser")

        iam.Role(self, "id_1234", role_name="lambda-apigateway-role", assumed_by=user)

        repo_dir = Path(__file__).parents[2]

        requirements_dir = build_requirements()

        base_api = _apigw.RestApi(self, "ApiGatewayWithCors", rest_api_name="ApiGatewayWithCors")

        base_lambda_layer = aws_lambda.LayerVersion(
            self,
            "base_layer",
            code=aws_lambda.Code.from_asset(str(requirements_dir)),
        )

        app_dir = repo_dir.joinpath("demo_app/demo_app")
        _, cdk_config, _ = gen_open_api_inspect(app_dir)

        self.add_resource(app_dir, base_api.root, base_lambda_layer, cdk_config)

    def add_resource(self, app_dir, resource, base_lambda_layer, config):

        for resource_name, resource_info in sorted(config["resources"].items()):

            new_resource = resource.add_resource(
                resource_name,
                default_cors_preflight_options=_apigw.CorsOptions(
                    allow_methods=list(resource_info.keys()), allow_origins=_apigw.Cors.ALL_ORIGINS
                ),
            )

            if "methods" in resource_info:
                for method, method_info in resource_info["methods"].items():
                    self.add_method(method, method_info, new_resource, app_dir, base_lambda_layer)

            if "resources" in resource_info:
                self.add_resource(app_dir, new_resource, base_lambda_layer, resource_info)

    def add_method(self, method, method_info, resource, app_dir, base_lambda_layer):
        func = aws_lambda.Function(
            self,
            method_info["function_name"],
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler=method_info["reference"],
            layers=[base_lambda_layer],
            code=aws_lambda.Code.from_asset(
                str(app_dir),
            ),
        )

        api_gw_lambda = _apigw.LambdaIntegration(
            func,
            proxy=True,
            integration_responses=[
                _apigw.IntegrationResponse(
                    status_code=method_info["status_code"],
                    response_parameters={"method.response.header.Access-Control-Allow-Origin": "'*'"},
                )
            ],
        )

        resource.add_method(
            method.upper(),
            api_gw_lambda,
            method_responses=[
                _apigw.MethodResponse(
                    status_code=method_info["status_code"],
                    response_parameters={"method.response.header.Access-Control-Allow-Origin": True},
                )
            ],
        )
