from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, AsyncIterable, Dict, Generic, Optional, Tuple, TypeVar
from uuid import UUID

from kilroy_face_py_shared import Metadata
from kilroy_server_py_utils import Configurable, JSONSchema

StateType = TypeVar("StateType")


class Face(Configurable[StateType], Generic[StateType], ABC):
    @property
    @abstractmethod
    def metadata(self) -> Metadata:
        pass

    @property
    @abstractmethod
    def post_schema(self) -> JSONSchema:
        pass

    @abstractmethod
    async def post(self, post: Dict[str, Any]) -> UUID:
        pass

    @abstractmethod
    async def score(self, post_id: UUID) -> float:
        pass

    @abstractmethod
    def scrap(
        self,
        limit: Optional[int] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
    ) -> AsyncIterable[Tuple[UUID, Dict[str, Any]]]:
        pass
