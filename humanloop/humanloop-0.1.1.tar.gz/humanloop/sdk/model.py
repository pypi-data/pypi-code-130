from humanloop.api.models.model import ModelConfig, ModelConfigResponse
from humanloop.sdk.init import _get_client


def register(model_config: ModelConfig) -> ModelConfigResponse:
    """ Register a new model configuration for a project and optionally tag it with
    an experiment.
    If the project does not exist, a new project with the provided name will be
    automatically created.
    """
    client = _get_client()
    return client.register(model_config)