from pydantic import Field, BaseModel
from typing import Optional
import datetime
from .log import KeyValues


class ModelConfig(BaseModel):
    name: Optional[str] = Field(
        title="Config name",
        description="A friendly display name for config. If not provided a name "
        "will be generated.",
    )
    project: str = Field(
        title="Project name",
        description="Unique project name. If it does not exist, a new project will "
        "be created.",
    )
    experiment: Optional[str] = Field(
        title="Experiment tag",
        description="Include a model configuration in an experiment group. "
        "Experiment groups are used for A/B testing and optimizing "
        "hyper-parameters.",
    )
    model: str = Field(
        title="Type of model used",
        description="What model type was used for the generation? e.g. text-davinci-002. "
    )
    prompt_template: Optional[str] = Field(
        title="Prompt template",
        description="Prompt template that incorporated your specified inputs to form "
        "your final request to the model.",
    )
    parameters: Optional[KeyValues] = Field(
        title="Model parameters",
        description="The hyper-parameter settings that along with your model source "
        "and prompt template (if provided) will uniquely determine a model"
        " configuration on Humanloop. For example the temperature setting.",
    )


class ModelConfigResponse(BaseModel):
    id: str
    display_name: str
    model_name: str
    prompt_template: Optional[str]
    parameters: Optional[dict]
    created_at: datetime.datetime
