from pathlib import Path

from azureml.core import (
    Dataset,
    Environment,
    Experiment,
    ScriptRunConfig,
    Workspace,
)
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core.runconfig import MpiConfiguration, DockerConfiguration
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.tensorboard import Tensorboard
from tabulate import tabulate


available_instances = {
    "1xK80": "Standard_NC6",
    "2xK80": "Standard_NC12",
    "4xK80": "Standard_NC24",
    "1xM60": "Standard_NV6",
    "2xM60": "Standard_NV12",
    "4xM60": "Standard_NV24",
    "1xV100": "Standard_NC6s_v3",
    "2xV100": "Standard_NC12s_v3",
    "4xV100": "Standard_NC24s_v3",
    "8xV100": "Standard_ND40rs_v2",
    "CPU": "STANDARD_DS11_V2",  # "Standard_D8_v3",
}


def get_environment(workspace, environment_name: str, requirements_file: Path):

    if not requirements_file.exists():
        raise RuntimeError(f"Given requirements file '{requirements_file}' does not exist at the provided path")
    elif requirements_file.name.endswith(".txt"):
        env = Environment.from_pip_requirements(environment_name, requirements_file)
    elif requirements_file.name.endswith(".yml"):
        env = Environment.from_conda_specification(environment_name, requirements_file)
    else:
        print("Couldn't resolve env from requirements file")

    return env


def get_inferred_instance(gpu_type: str, num_gpus: int):
    if gpu_type is None or gpu_type == "CPU":
        return available_instances.get("CPU")
    instance = available_instances.get(f"{num_gpus}x{gpu_type}")
    assert instance is not None, f"Could not look up inferred instance w/ Num GPUs: {num_gpus} and GPU Type: {gpu_type}"
    return instance


def find_or_create_compute_target(
    workspace,
    name,
    vm_size="STANDARD_NC6",
    min_nodes=0,
    max_nodes=1,
    idle_seconds_before_scaledown=1200,
    vm_priority="lowpriority",
):

    if name in workspace.compute_targets:
        return ComputeTarget(workspace=workspace, name=name)
    else:
        config = AmlCompute.provisioning_configuration(
            vm_size=vm_size,
            min_nodes=min_nodes,
            max_nodes=max_nodes,
            vm_priority=vm_priority,
            idle_seconds_before_scaledown=idle_seconds_before_scaledown,
        )
        target = ComputeTarget.create(workspace, name, config)
        target.wait_for_completion(show_output=True)
    return target


def submit_basic_run(
    script,
    script_args,
    workspace_config="./config.json",
    target_name="my-cluster",
    gpu_type="K80",
    num_gpus=1,
    min_nodes=0,
    max_nodes=10,
    num_nodes=1,
    dataset_name=None,
    dataset_mount_dir="/dataset",
    experiment_name="fuego-experiments",
    environment_name='my-env',
    requirements_file="./requirements.txt",
    docker_image="mcr.microsoft.com/azureml/openmpi4.1.0-cuda11.3-cudnn8-ubuntu20.04",
    subscription_id=None,
    resource_group=None,
    workspace_name=None,
    tenant_id=None,
    client_id=None,
    client_secret=None,
):
    do_use_service_principal = all([tenant_id, client_id, client_secret])
    if do_use_service_principal:
        auth = ServicePrincipalAuthentication(
            tenant_id=tenant_id,
            service_principal_id=client_id,
            service_principal_password=client_secret,
        )
    else:
        auth = None


    do_use_config_file = not all([subscription_id, resource_group, workspace_name])
    if do_use_config_file:
        ws = Workspace.from_config(workspace_config, auth=auth)
    else:
        ws = Workspace(
            subscription_id=subscription_id,
            resource_group=resource_group,
            workspace_name=workspace_name,
            auth=auth
        )

    compute_target = find_or_create_compute_target(
        ws, target_name, get_inferred_instance(gpu_type, num_gpus), min_nodes, max_nodes
    )

    # Get/Create the environment + specify docker image/configuration.
    env = get_environment(ws, environment_name, requirements_file)
    docker_config = DockerConfiguration(use_docker=True)
    env.docker.base_image = docker_image

    run_config = ScriptRunConfig(
        source_directory=Path(script).parent,
        script=Path(script).name,
        arguments=script_args,
        compute_target=compute_target,
        environment=env,
        distributed_job_config=MpiConfiguration(process_count_per_node=1, node_count=num_nodes),
        docker_runtime_config=docker_config,
    )
    if dataset_name is not None:
        ds = ws.datasets.get(dataset_name)
        run_config.run_config.data = {ds.name: ds.as_mount(dataset_mount_dir)}

    run = Experiment(ws, experiment_name).submit(run_config)
    return run


def list_datasets(workspace_config: Path):
    ws = Workspace.from_config(workspace_config)
    names, versions, dates = [], [], []
    for ds_name in ws.datasets:
        names.append(ds_name)

    print(
        tabulate(
            {"Datasets": names},
            headers="keys",
            tablefmt="github",
        )
    )


def create_dataset(workspace_config, source_dir, name, description=None, overwrite=False):
    ws = Workspace.from_config(workspace_config)
    datastore = ws.get_default_datastore()
    datastore.upload(
        src_dir=source_dir,
        target_path=name,
        overwrite=overwrite,
        show_progress=True,
    )
    _ = Dataset.File.from_files(path=[(datastore, name)]).register(
        workspace=ws,
        name=name,
        description=description,
        create_new_version=True,
    )


def create_tensorboard(workspace_config, experiment_name):
    ws = Workspace.from_config(workspace_config)
    exp = Experiment(ws, experiment_name)
    tb = Tensorboard([*exp.get_runs()])
    tb.start()
    print("Check out your Tensorboard at: http://localhost:6006")

    while True:
        input_data = input("Stop the tensorboard server? [y]")
        if input_data in ['y']:
            break

    tb.stop()
