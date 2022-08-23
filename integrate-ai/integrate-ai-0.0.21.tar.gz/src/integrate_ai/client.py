import typer
import os
import rich
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn
from integrate_ai.utils.docker_client import DockerClient
from pathlib import Path
from integrate_ai.utils.typer_utils import TogglePromptOption, cast_path_to_dict
import os

batch_size_default = 16
instruction_polling_time_default = 30
log_interval_default = 10

app = typer.Typer(no_args_is_help=True)


@app.command()
def pull(
    token: str = TogglePromptOption(
        ...,
        help="The IAI token.",
        prompt="Please provide your IAI token",
        envvar="IAI_TOKEN",
    ),
    version: str = typer.Option("latest", "--version", "-v", help="The version of the docker image to pull."),
    GPU: bool = typer.Option(False, "--GPU/--CPU", help="Specify the GPU or CPU version of the docker image."),
):
    """
    Pull the federated learning docker client.\n Defaults to the latest CPU version. Docker must be running for this command to work.
    """

    no_prompt = os.environ.get("IAI_DISABLE_PROMPTS")
    delete_response = False

    # start progress bar
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:

        # connect to docker
        p = progress.add_task(description="Connecting to docker...", total=1)
        docker_client = DockerClient(token, gpu=GPU)
        progress.update(task_id=p, completed=True)

        # check if any existing docker images on system
        p = progress.add_task(description="Searching for existing client images...", total=1)
        current_images = docker_client.get_local_versions(docker_client.docker_image_name)
        progress.update(task_id=p, completed=True)

        # check for latest docker image
        p = progress.add_task(description="Determining latest available client version...", total=1)
        docker_client.login()
        latest_available_version = docker_client.get_latest_available_version()
        progress.update(task_id=p, completed=True)

    version_to_pull = latest_available_version if version == "latest" else version
    if len(current_images) == 0:
        rprint("No existing client version found on system.")
    else:

        # if images exist on system, check the latest version that is installed
        latest_version = docker_client.get_latest_version_of_image(current_images) or "`latest`"
        if not GPU and "-cpu" not in version_to_pull:
            version_to_pull += "-cpu"

        rprint(
            f"Latest version of docker image found on system is {latest_version}. Most recent version is {latest_available_version}."
        )

        if latest_version == version_to_pull:

            # no point installing if they already have the latest image
            rprint("The requested version of the client image is already on your system. Exiting...")
            raise typer.Exit(0)
        else:
            prompt_msg = f"A newer version {latest_available_version} was found. The current version of the client image will be deleted from your system. Do you want to proceed?"
            # confirm that they are ok with deleting current client images on system
            prompt_msg = "Installing this client image will delete any current version of this image on your system. Do you want to proceed?"
            if no_prompt:
                delete_response = True
            else:
                delete_response = typer.confirm(prompt_msg)

    # delete current client images if they ok'd it
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        if delete_response:
            p = progress.add_task(
                description="Yes response received. Deleting existing client images...",
                total=1,
            )
            docker_client.delete_images(current_images)
            progress.update(task_id=p, completed=True)
        elif not delete_response and len(current_images) > 0:
            rprint("`No` response received. Exiting...")
            raise typer.Exit(0)

    # login and pull docker image
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        p = progress.add_task(description="Logging into docker repo...", total=1)
        login_result = docker_client.login()
        progress.update(task_id=p, completed=True)
        p = progress.add_task(
            description=f"Pulling docker image {version_to_pull}. This will take a few minutes...",
            total=1,
        )
        pull_result = docker_client.pull(repo=docker_client.docker_image_name, tag=version_to_pull)
        progress.update(task_id=p, completed=True)
        rprint(f"Image {version_to_pull} is now available.")
        raise typer.Exit(0)


@app.command()
def version():
    """
    The currently installed version of the docker client image.
    """
    docker_client = DockerClient()
    current_images = docker_client.get_local_versions(docker_client.docker_image_name)
    latest_version = docker_client.get_latest_version_of_image(current_images)
    if len(current_images) == 0:
        rprint("No client image found on system.")
    elif not latest_version:
        rprint("Found version tagged as `latest`.")
    else:
        rprint(latest_version)


@app.command()
def list(
    token: str = TogglePromptOption(
        ...,
        help="The IAI token.",
        prompt="Please provide your IAI token",
        envvar="IAI_TOKEN",
    )
):
    """
    List all available docker client images versions to pull.
    """
    docker_client = DockerClient(token)
    docker_client.login()
    versions = docker_client.get_versions()
    rprint("\n".join(versions))


# @app.command()
def log():
    """
    This command enables logging of the client docker container for debugging purposes.
    """
    pass  # pragma: no cover


@app.command()
def train(
    token: str = TogglePromptOption(
        ...,
        help="Your generated IAI token.",
        prompt="Please provide your IAI token.",
        envvar="IAI_TOKEN",
    ),
    session: str = TogglePromptOption(
        ...,
        help="The session id to join for training.",
        prompt="Please provide the training session id.",
        envvar="IAI_SESSION",
    ),
    train_path: Path = TogglePromptOption(
        ...,
        help="Training dataset path.",
        prompt="Please provide the training dataset path",
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
    test_path: Path = TogglePromptOption(
        ...,
        help="Testing dataset path.",
        prompt="Please provide the testing dataset path",
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
    client_name: str = TogglePromptOption(
        ...,
        help="The name used for client container",
        prompt="Please provide the client container name.",
    ),
    batch_size: int = typer.Option(batch_size_default, "--batch-size", help="Batch size to load the data with."),
    instruction_polling_time: int = typer.Option(
        instruction_polling_time_default,
        "--instruction-polling-time",
        help="Time to wait for new instructions in seconds.",
    ),
    log_interval: int = typer.Option(
        log_interval_default,
        "--log-interval",
        help="The logging frequency for training printout. ",
    ),
    approve_custom_package: bool = typer.Option(
        False,
        "--approve-custom-package",
        help="Flag to give pre-approval for training custom model package.",
    ),
    remove_after_complete: bool = typer.Option(
        False,
        "--remove-after-complete",
        help="Flag to remove container after training completed",
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enables debug logging."),
):
    """
    Join a training session using the docker client.
    The client docker container will be deleted on completion.
    """
    docker_client = DockerClient()
    current_images = docker_client.get_local_versions(docker_client.docker_image_name)
    latest_version = docker_client.get_latest_version_of_image(current_images)

    mount_path = "/root/"
    train_path_dict = cast_path_to_dict(train_path)
    test_path_dict = cast_path_to_dict(test_path)

    if len(current_images) == 0:
        rich.print("No client image found on system.")
        rich.print("Exiting...")
        raise typer.Exit(0)

    image_name = f"{docker_client.docker_image_name}"
    if latest_version:
        image_name += ":" + latest_version

    volumes = {}
    volumes[train_path_dict["parent_path"]] = {"bind": mount_path + train_path_dict["parent_dir"], "mode": "ro"}
    volumes[test_path_dict["parent_path"]] = {"bind": mount_path + test_path_dict["parent_dir"], "mode": "ro"}
    mounted_train_path = train_path_dict["full_path"].replace(
        train_path_dict["parent_path"], mount_path + train_path_dict["parent_dir"]
    )
    mounted_test_path = test_path_dict["full_path"].replace(
        test_path_dict["parent_path"], mount_path + test_path_dict["parent_dir"]
    )

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        container_name = str(client_name)

        start_container_task = progress.add_task(description=f"Starting container {container_name}...", total=1)
        try:
            response = docker_client.run(
                image_name,
                detach=True,
                options={
                    "tty": True,
                    "name": container_name,
                    "volumes": volumes,
                },
            )
        except Exception as e:
            progress.console.print(e, style="red")
            raise typer.Exit(0)

        progress.update(task_id=start_container_task, completed=True)
        progress.console.print(f"Container {container_name} is started.", style="green")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        start_training_task = progress.add_task(description=f"Training...", total=1)
        container = docker_client.get_container(container_name)

        cmd = f"hfl train --token {token} --session-id {session}"
        cmd += f" --train-path {mounted_train_path}"
        cmd += f" --test-path {mounted_test_path}"
        cmd += f" --batch-size {batch_size}"
        cmd += f" --instruction-polling-time {instruction_polling_time}"
        cmd += f" --log-interval {log_interval}"
        if approve_custom_package:
            cmd += " --approve-custom-package"

        response = container.exec_run(cmd, stdout=verbose, stream=True, demux=True)
        if response:
            for (output, error) in response.output:  # type: ignore
                if error:
                    progress.console.print(error.decode("utf-8"))
                else:
                    progress.console.print(output.decode("utf-8"))

        progress.update(task_id=start_training_task, completed=True)

    progress.console.print(f"Finished training.", style="green")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        closing_task = progress.add_task(description=f"Closing container...", total=1)
        container.stop()
        if remove_after_complete:
            container.remove()
        progress.update(task_id=closing_task, completed=True)

        raise typer.Exit(0)


@app.callback()
def main():
    """
    Sub command for managing client related operations.
    """
