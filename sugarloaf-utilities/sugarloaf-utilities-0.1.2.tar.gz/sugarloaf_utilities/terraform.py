from multiprocessing.sharedctypes import Value
from os import getcwd
from pathlib import Path
from subprocess import run
from typing import List, Optional

from click import (
    Choice as ClickChoice,
    Path as ClickPath,
    command,
    option,
    secho,
)

from sugarloaf_utilities.components import get_ordered_packages
from sugarloaf_utilities.io import EchoSubprocess
from sugarloaf_utilities.template import GenerateTemplate


def find_parent_config_path(child_path: str) -> Path:
    # Traverse up the filepath until we find a .sugarloaf folder
    # that contains a configuration file
    child_path = Path(child_path)
    while child_path is not None:
        if (child_path / ".sugarloaf").exists():
            return child_path
        child_path = child_path.parent
    raise ValueError("No .sugarloaf configuration folder found in any parent directories.")


def should_init(message) -> bool:
    """
    Given the `stderr` response from a terraform execution, attempt to determine
    whether any of these errors are init related. If so we should re-initialize the module.

    """
    # If we see these errors during apply, it means we need to re-init our directory
    init_errors = [
        "Required plugins are not installed",
        "Module not installed",
        "Inconsistent dependency lock file",
        "The source address was changed",
        # Fallback - terraform usually hints to update the files
        "Run \"terraform init\""
    ]

    return any(
        error_text in message.replace("\n", " ")
        for error_text in init_errors
    )

def run_chained_terraform(apply_path, command: str, subset: Optional[List[str]], auto_approve: bool):
    packages = get_ordered_packages()
    package_names = {package.name for package in packages}

    if subset:
        # Determine if we were provided allowable entries
        missing_subset = [item for item in subset if item not in package_names]
        if missing_subset:
            secho(f"{missing_subset} are not valid packages, only supported: {package_names}", fg="red")
            return
        packages = [package for package in packages if package.name in subset]

    missing_packages = []
    for package in packages:
        if not (apply_path / package.name).exists():
            missing_packages.append(package.name)
    if missing_packages:
        secho(f"Packages not found: {missing_packages}", fg="red")
        return

    for package in packages:
        secho(f"Executing package: `{package.name}`...", fg="yellow")

        # Do the short setup, assuming we have already inited the parent container.
        # If we catch any errors that have to do with initializing we fallback to running the init
        response_apply = EchoSubprocess(["terraform", f"-chdir={(apply_path / package.name)}", command, "-auto-approve" if auto_approve else ""]).run()
        if response_apply.returncode != 0:
            # Attempt to see whether any of these errors are init related
            if not should_init(response_apply.stderr):
                # NOTE: Encountering this error might mean we need to expand our `INIT_ERRORS` constant with
                # further error codes that are related to non-inited packages
                # Since we rely on string matching we know our approach is a bit fuzzy
                secho(f"Plan failed for module `{package.name}`, permanent error. Aborting...", fg="red")
                return
        else:
            secho("Success", fg="green")
            continue

        # Do the full setup
        secho(f"Running init and apply for `{package.name}`", fg="yellow")
        response_init = EchoSubprocess(["terraform", f"-chdir={(apply_path / package.name)}", "init"]).run()
        if response_init.returncode != 0:
            secho(f"Init failed for module `{package.name}`, aborting...", fg="red")
            return
        response_apply = run(["terraform", f"-chdir={(apply_path / package.name)}", "apply", "-auto-approve" if auto_approve else ""])
        if response_apply.returncode != 0:
            secho(f"Plan failed for module `{package.name}`, aborting...", fg="red")
            return
        secho("Success", fg="green")


@command()
@option("--path", type=ClickPath(exists=True, file_okay=False, dir_okay=True), required=False)
@option("--subset", type=str, multiple=True, required=False)
@option("--debug", is_flag=True, default=False)
@option("-auto-approve", is_flag=True, default=False)
def chain_apply(path: Optional[str], subset: Optional[List[str]], auto_approve: bool, debug: bool):
    """
    Chained apply that "terraform apply" our packages in dependency order, by default requesting
    clients confirm each change that is applied. To override and have it accept changes by default, pass
    the -auto-approve flag. We will halt on any plan failure before attempting to run the next ones in the
    dependency graph.

    Will attempt to apply in the local directory. If all packages specified in the DAG definition
    are not found, will throw an error.

    :param debug: If this flag is provided, will refresh the template during every run. Useful for
    local debugging of the `sugarloaf-infrastructure` codebase.

    """
    current_path = Path(path) if path else Path(getcwd())

    if not (current_path / ".sugarloaf/config.json").exists():
        secho("Must be run in root project directory", fg="red")
        return

    # Generate new build configuration based on the latest core files
    if debug:
        #project_root = find_parent_config_path(current_path)
        secho("Debug: generating new templates...\n", fg="yellow")
        template_generator = GenerateTemplate()
        template_generator(current_path, current_path / "override", confirm_delete=False)
        secho("\n")

    apply_path = current_path / "build-infrastructure"

    run_chained_terraform(apply_path, "apply", subset, auto_approve)


@command()
@option("--path", type=ClickPath(exists=True, file_okay=False, dir_okay=True), required=False)
@option("--subset", type=ClickChoice([package.name for package in get_ordered_packages()]), multiple=True, required=False)
@option("-auto-approve", is_flag=True, default=False)
def chain_destroy(path: Optional[str], subset: Optional[List[str]], auto_approve: bool):
    """
    Chained destroy, will tear down resources in the opposite order that they are created. Accepts
    the same parameters as chain_apply.

    """
    current_path = Path(path) if path else Path(getcwd())

    if not (current_path / ".sugarloaf/config.json").exists():
        secho("Must be run in root project directory", fg="red")
        return

    apply_path = current_path / "build-infrastructure"

    run_chained_terraform(apply_path, "destroy", subset, auto_approve)
