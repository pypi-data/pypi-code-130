import boto3
from box import Box
from mypy_boto3_cloudformation import CloudFormationClient


def outputs_to_dict(outputs):
    return dict(map(lambda x: (x["OutputKey"], x["OutputValue"]), outputs))


def ensure_path(outputs, elements):
    path = "root"
    for el in elements:
        if el not in outputs[path]:
            outputs[path][el] = {}

        path += "." + el


def get_stack_outputs(stack_name, region):
    client: CloudFormationClient = boto3.client("cloudformation", region_name=region)
    root_stack = client.describe_stacks(StackName=stack_name)["Stacks"][0]

    outputs = Box(box_dots=True)
    outputs["root"] = outputs_to_dict(root_stack.get("Outputs"))

    paginator = client.get_paginator("list_stacks")
    for page in paginator.paginate(
            StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE"], PaginationConfig={"MaxItems": 500}
    ):
        for stack in page["StackSummaries"]:
            if stack.get("RootId", None) == root_stack["StackId"]:
                nested_stack = client.describe_stacks(StackName=stack.get("StackName"))["Stacks"][0]

                path = nested_stack.get("StackName").replace(root_stack.get("StackName"), "").strip("-").split("-")[::2]
                ensure_path(outputs, path)
                outputs["root." + ".".join(path)].update(outputs_to_dict(nested_stack.get("Outputs", [])))

    return outputs


def resolve_vars(mapping, outputs):
    vars = {}
    for key, path in mapping.items():
        vars[key] = outputs[path]

    return vars
