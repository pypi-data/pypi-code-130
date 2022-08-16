import json
import logging
import tarfile
import tempfile
from typing import Any, Callable, Optional, Tuple

from colorama import Fore, Style
from truss.build import mk_truss
from truss.truss_handle import TrussHandle

import baseten
from baseten.baseten_deployed_model import BasetenDeployedModel
from baseten.common import api
from baseten.common.core import MODEL_FILENAME, Semver, raises_api_error
from baseten.common.settings import API_URL_BASE
from baseten.common.util import base64_encoded_json_str

logger = logging.getLogger(__name__)


def _exists_model(
    model_name: Optional[str],
    model_id: Optional[str],
    models_provider: Callable
) -> Optional[Tuple[str, str]]:
    """Checks if an effective model exists for the purpose of deploy or one needs to be created.

    If model name is supplied and a model with that name exists then it's picked up. Otherwise
    working model id in the session is tried.

    Returns id of model if model exists, or None
    """
    models = models_provider()["models"]
    model_id_by_name = {model["name"]: model["id"] for model in models}
    model_name_by_id = {model["id"]: model["name"] for model in models}

    if model_name is not None:
        if model_name in model_id_by_name:
            return model_id_by_name[model_name], model_name
        else:
            logger.warning("Model name not found in deployed models")
            return None

    # No model_name supplied, try to work with working model id
    if model_id is not None:
        if model_id in model_name_by_id:
            return model_id, model_name_by_id[model_id]
        else:
            logger.warning("Working model id not found in deployed models")
            return None

    # No model name or working model
    return None


def build_truss(
    model: Any,
    target_directory: str = None,
) -> TrussHandle:
    """
    Builds truss into target directory from in-memory model
    Args:
        model (an in-memory model object): A model object to be deployed (e.g. a keras,
            sklearn, or pytorch model object)
        target_directory (str, optional): The local directory target for the truss.
            Otherwise a temporary directory will be generated
    Returns:
        TrussHandle
    """

    if target_directory:
        logger.info(
            "Your model docker build directory is all set up at {target_directory}"
        )
        logger.info(
            f"To create image context: baseten truss build-context [BUILD_DIR] {target_directory}"
        )
        logger.info(
            f"To build image: baseten truss build-image {target_directory} [BUILD_DIR]"
        )
        logger.info(
            f"To run image: baseten truss run-image {target_directory} [BUILD_DIR]"
        )
    return mk_truss(model=model, target_directory=target_directory)


@raises_api_error
def deploy_truss(
    b10_truss: TrussHandle,
    model_name: str = None,
    semver_bump: Semver = Semver.MINOR.value,
) -> BasetenDeployedModel:
    """
    Given an existing baseten truss object, deploy it onto the baseten infastructure.

    Args:
        b10_truss: A truss object representing a local baseten_truss directory
        model_name (str, optional): The name of the model to be created, if necessary.
        semver_bump (str, optional): The version bump for this deployment, one of 'MAJOR', 'MINOR', 'PATCH'.

    Returns:
        BasetenDeployedModel
    """
    if model_name is None:
        import coolname
        model_name = coolname.generate_slug(2)

    elif not model_name or model_name.isspace():
        raise ValueError("Model Names cannot be empty or spaces")

    logger.info(f"Serializing {Fore.BLUE}{model_name}{Style.RESET_ALL} truss.")
    temp_file = _compress_truss(b10_truss=b10_truss)
    model_info = _exists_model(model_name, baseten.working_model_id, api.models)

    logger.info("Making contact with BaseTen 👋 👽")
    s3_key = api.upload_model(temp_file, "tgz", MODEL_FILENAME)
    # String that can be passed through graphql api
    config = base64_encoded_json_str(b10_truss._spec._config.to_dict())

    if not model_info:
        model_id, model_version_id = create_model_from_s3(
            model_name, s3_key, config, semver_bump
        )
        logger.info(
            f"Successfully registered model {Fore.BLUE}{model_name}{Style.RESET_ALL}."
        )
    else:
        model_id, model_name = model_info
        model_version_id = create_model_version_from_s3(model_id, s3_key, config, semver_bump)
        logger.info(
            f"Successfully created version {Fore.BLUE}{model_version_id}{Style.RESET_ALL} for {model_name}."
        )

    _generate_model_deploy_logs(model_id)
    return BasetenDeployedModel(
        model_version_id=model_version_id, model_name=model_name
    )


def create_model_from_s3(model_name, s3_key, config, semver_bump):
    model_version_json = api.create_model_from_truss(
        model_name=model_name,
        s3_key=s3_key,
        config=config,
        semver_bump=semver_bump,
        client_version=baseten.__version__
    )

    logger.info(
        f"Created model:\n{json.dumps(model_version_json, indent=4)}"
    )
    model_id = model_version_json["id"]
    model_version_id = model_version_json["version_id"]
    # Set the newly created model model_version_json
    # be the working model for future commands
    baseten.working_model_id = model_id

    return model_id, model_version_id


def create_model_version_from_s3(model_id, s3_key, config, semver_bump):
    model_version_json = api.create_model_version_from_truss(
        model_id=model_id,
        s3_key=s3_key,
        config=config,
        semver_bump=semver_bump,
        client_version=baseten.__version__
    )
    logger.info(config)

    model_version_id = model_version_json["id"]
    return model_version_id


def _generate_model_deploy_logs(model_id):
    logger.info(f"{Fore.BLUE} Deploying model version.")
    model_version_web_url = f"{API_URL_BASE}/models/{model_id}"
    logger.info("🏁 The model is being built and deployed right now 🏁")
    visit_message = f"|  Visit {Fore.BLUE}{model_version_web_url}{Style.RESET_ALL} for deployment status  |"
    visit_message_len = len(visit_message) - len(Fore.BLUE) - len(Style.RESET_ALL)
    logger.info("".join(["-" for _ in range(visit_message_len)]))
    logger.info(visit_message)
    logger.info("".join(["-" for _ in range(visit_message_len)]))


def _compress_truss(b10_truss):
    temp_file = tempfile.NamedTemporaryFile(suffix=".tgz")
    with tarfile.open(temp_file.name, "w:gz") as tar:
        tar.add(b10_truss._spec.truss_dir, arcname=".")
    temp_file.file.seek(0)
    return temp_file


def build_and_deploy_truss(
    model: Any,
    model_name: str = None,
    version_bump=Semver.MINOR.value,
) -> BasetenDeployedModel:
    truss = build_truss(model)
    return deploy_truss(truss, model_name, version_bump)


def pull_model(model_version_id: str, directory: str = "."):
    deployed_model = BasetenDeployedModel(model_version_id=model_version_id)
    return deployed_model.pull(directory)
