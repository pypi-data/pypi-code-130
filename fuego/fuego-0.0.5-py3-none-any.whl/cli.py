from enum import Enum
from pathlib import Path

import typer

from .azml_utils import submit_basic_run

app = typer.Typer()


class GPUType(str, Enum):
    k80 = "K80"
    m60 = "M60"
    v100 = "V100"
    none = "CPU"


def num_gpus_callback(ctx: typer.Context, param: typer.CallbackParam, value: int):
    if value not in [0, 1, 2, 4]:
        raise typer.BadParameter("Num GPUs choice must be 1, 2, or 4.")
    return value


@app.command(
    name="run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run(
    ctx: typer.Context,
    script: Path,
    workspace_config: Path = typer.Option(
        "./config.json",
        help="AzureML resource config.json file. Download from Azure portal by going to your resource's page and selecting 'Download config.json'",
    ),
    target_name: str = typer.Option(
        "my-cluster",
        help="The name of the compute cluster to run your script on. If it doesn't exist, we'll create it for you.",
    ),
    gpu_type: GPUType = typer.Option(
        GPUType.k80,
        help="The type of GPU you'd like to be on your cluster. Pass 'CPU' if you don't require a GPU.",
        case_sensitive=False,
    ),
    num_gpus: int = typer.Option(
        1,
        callback=num_gpus_callback,
        help="Number of GPUs per node. Can be 1, 2, or 4. If --gpu_type is CPU, this argument will be ignored, effectively setting it to 0.",
    ),
    min_nodes: int = 0,
    max_nodes: int = 10,
    num_nodes: int = 1,
    dataset_name: str = None,
    dataset_mount_dir: Path = "/dataset",
    experiment_name: str = "fuego-experiments",
    environment_name: str = "fuego-env",
    requirements_file: Path = "./requirements.txt",
    docker_image: str = "mcr.microsoft.com/azureml/openmpi4.1.0-cuda11.3-cudnn8-ubuntu20.04",
    subscription_id: str = None,
    resource_group: str = None,
    workspace_name: str = None,
    tenant_id: str = None,
    client_id: str = None,
    client_secret: str =None,
):
    if not script.exists():
        raise RuntimeError(f"Script file '{script}' does not exist")

    if not all([subscription_id, resource_group, workspace_name]) and not workspace_config.exists():
        raise RuntimeError(
            "Either --subscription_id, --resource_group, and --workspace_name must be provided, or --workspace_config must point to a valid AzureML config.json file."
        )
    
    if not requirements_file.exists():
        raise RuntimeError(f"Requirements file '{requirements_file}' does not exist")

    submit_basic_run(
        script,
        ctx.args,
        workspace_config,
        target_name,
        gpu_type,
        num_gpus,
        min_nodes,
        max_nodes,
        num_nodes,
        dataset_name,
        str(dataset_mount_dir),
        experiment_name,
        environment_name,
        requirements_file,
        docker_image,
        subscription_id,
        resource_group,
        workspace_name,
        tenant_id,
        client_id,
        client_secret,
    )


@app.command(name="create_dataset")
def create(source_dir: Path, name: str = None, description: str = None, workspace_config: Path = "./config.json"):
    from .azml_utils import create_dataset

    if source_dir is None:
        RuntimeError("You must provide a source_dir")

    print(f"{source_dir} | {name} | {description} | {workspace_config}")
    create_dataset(str(workspace_config), str(source_dir), name, description=None, overwrite=False)


@app.command(name="list_datasets")
def datasets_list(workspace_config: Path = "./config.json"):
    from .azml_utils import list_datasets

    list_datasets(workspace_config)


@app.command(name="tensorboard")
def tensorboard_create(workspace_config: Path = "./config.json", experiment_name: str = "fuego-experiments"):
    from .azml_utils import create_tensorboard

    create_tensorboard(workspace_config, experiment_name)


if __name__ == "__main__":
    app()
