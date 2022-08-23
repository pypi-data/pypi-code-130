import os
import subprocess
from os import getcwd
from os.path import join, isdir, isfile

import boto3
import click
import inquirer as inquirer
import yaml
from mypy_boto3_appsync.client import AppSyncClient

from amplify_cf.ext import common_options


@click.group()
def schema():
    pass


@schema.command(name="fetch")
@click.argument("api", required=False)
@common_options
@click.pass_obj
def fetch_schema(obj, api=None):
    try:
        appsync: AppSyncClient = boto3.client("appsync", region_name=obj.region)
    except:
        click.secho("Failed to obtain AWS credentials", fg="red")
        return 1

    if not api:
        apis = dict(map(lambda x: (x["name"], x["apiId"]), appsync.list_graphql_apis().get("graphqlApis", [])))
        questions = [
            inquirer.List(
                "api",
                message="Which API you would like to export?",
                choices=apis.keys(),
            ),
        ]
        answers = inquirer.prompt(questions)
        api_name = answers.get("api")
        api_id = apis.get(api_name)
    else:
        api_id = api

    graphql_config_file = join(getcwd(), ".graphqlconfig.yml")
    if isfile(graphql_config_file):
        with open(graphql_config_file, "r") as f:
            graphql_config = yaml.load(f, Loader=yaml.Loader)
            raw_api_name = list(graphql_config.get("projects").keys())[0]

    click.secho(f"Fetching schema for API: {api_id}", fg="green")
    schema = appsync.get_introspection_schema(apiId=api_id, format="SDL", includeDirectives=True)

    work_dir = getcwd()
    target_dir = join(work_dir, "amplify", "backend", "api", raw_api_name, "build")
    if not isdir(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    target_file = join(target_dir, "schema.graphql")
    with open(target_file, "wb+") as f:
        f.write(schema.get("schema").read())

    click.secho(f"Saved schema to: {target_file}", fg="green")


@schema.command(name="update")
@click.argument("api", required=False)
@common_options
@click.pass_context
def update_models(ctx, api):
    result = ctx.invoke(fetch_schema, api=api)

    if result not in [0, None]:
        return result

    amplify_path = "./node_modules/.bin/amplify"
    if not isfile(amplify_path):
        click.secho("Missing local amplify installation. Trying with global", fg="yellow")
        amplify_path = "amplify"

    if not isfile("./schema.json"):
        open("./schema.json", "w+")
        p = subprocess.call([amplify_path, "codegen"], env=os.environ)

        os.unlink("./schema.json")
