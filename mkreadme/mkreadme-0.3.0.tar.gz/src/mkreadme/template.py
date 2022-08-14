import os
from typing import Iterator

from pydantic import BaseModel, Extra, constr
from pydantic.typing import List
from yaml import FullLoader, load  # type: ignore

BASE_DIR = os.path.dirname(__file__)
DEFAULT_CONFIG_DIR = os.path.join(BASE_DIR, "static", "template.yml")


class _StrictBaseModel(BaseModel):
    class Config:
        extra = Extra.forbid


class SectionTemplate(_StrictBaseModel):
    name: str
    slug: str
    markdown: str
    icon: constr(min_length=1, max_length=3)  # type: ignore


class Templates(_StrictBaseModel):
    __root__: List[SectionTemplate]

    def __iter__(self) -> Iterator[SectionTemplate]:  # type: ignore
        return iter(self.__root__)

    def __getitem__(self, key: int) -> SectionTemplate:
        return self.__root__[key]

    def __len__(self) -> int:
        return len(self.__root__)


def load_templates() -> Templates:
    with open(DEFAULT_CONFIG_DIR, "r") as f:
        raw_config = load(f, Loader=FullLoader)
        return Templates.parse_obj(raw_config)
