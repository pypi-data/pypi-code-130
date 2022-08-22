import os
from argparse import ArgumentParser
from pathlib import Path
from shutil import copy2
from typing import Dict

from mlflow_deploy_cli.utils import (create_dot_env, populate_template,
                                     prompt_env_variables)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--backend-store", choices=["postgres"], type=str, default="postgres"
    )
    parser.add_argument(
        "--artifact-store",
        choices=["azure", "s3", "gcp", "local"],
        type=str,
        default="azure",
    )

    args = parser.parse_args()

    placeholders: Dict[str, str] = {}
    env_variables: Dict[str, str] = {}

    if args.backend_store == "postgres":
        env_variables.update(
            prompt_env_variables(
                [
                    "POSTGRESQL_USERNAME",
                    "POSTGRESQL_PASSWORD",
                    "POSTGRESQL_DATABASE",
                    "BACKEND_STORE_URI",
                ]
            )
        )
        username = env_variables["POSTGRESQL_USERNAME"]
        password = env_variables["POSTGRESQL_PASSWORD"]
        database = env_variables["POSTGRESQL_DATABASE"]

        env_variables.update(
            {
                "BACKEND_STORE_URI": f"postgresql://{username}:{password}@db:5432/{database}"
            }
        )

    if args.artifact_store == "azure":
        env_variables.update(
            prompt_env_variables(
                [
                    "AZURE_STORAGE_CONNECTION_STRING",
                    "AZURE_STORAGE_ACCESS_KEY",
                    "DEFAULT_ARTIFACT_ROOT",
                ]
            )
        )
        placeholders["artifact_storage_specific_requirements"] = " ".join(
            ["azure-storage-blob", "azure-identity"]
        )

    elif args.artifact_store == "s3":
        env_variables.update(
            prompt_env_variables(
                ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "DEFAULT_ARTIFACT_ROOT"]
            )
        )

    elif args.artifact_store == "gcp":
        env_variables.update(prompt_env_variables(["DEFAULT_ARTIFACT_ROOT"]))
        placeholders["artifact_storage_specific_requirements"] = "google-cloud-storage"

    elif args.arifact_store == "local":
        ...

    else:
        raise NotImplementedError(
            f"Artifact Store f{args.artifact_store} currently is not supported"
        )

    os.makedirs(os.path.join(os.getcwd(), "build"), exist_ok=True)
    populate_template(
        os.path.join(Path(__file__).parent, "template", "Dockerfile.template"),
        os.path.join(os.getcwd(), "build", "Dockerfile"),
        placeholders,
    )
    copy2(
        os.path.join(Path(__file__).parent, "template", "docker-compose.yml"),
        os.path.join(os.getcwd(), "build", "docker-compose.yml"),
    )
    create_dot_env(env_variables, os.path.join(os.getcwd(), "build"))
