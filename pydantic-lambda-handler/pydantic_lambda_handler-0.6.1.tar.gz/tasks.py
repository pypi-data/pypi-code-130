import json
import subprocess
from pathlib import Path

from invoke import task

from pydantic_lambda_handler.gen_open_api_inspect import gen_open_api_inspect

root = Path(__name__).parent
demo_app_dir = root.joinpath("demo_app")


@task
def build_and_deploy(c):
    subprocess.run("cdk bootstrap", check=True, shell=True, cwd=demo_app_dir)
    deploy(c)


@task
def deploy(c):
    subprocess.run("cdk deploy --require-approval never", check=True, shell=True, cwd=demo_app_dir)


@task
def generate_open_api_spec(c):
    path = Path(__file__).parent.joinpath("demo_app/demo_app")
    schema, *_ = gen_open_api_inspect(path)
    with path.joinpath("open_api_spec.json").open("w") as f:
        json.dump(schema, f, indent=4)
