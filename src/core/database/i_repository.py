from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar, Union

from src.core.configuration.configuration import config
from src.core.database.repository_registry import repository_registry

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    def _get_engine(self, identifier: str, is_vector: bool = False) -> Any:
        engine_type = config.get("DATABASE_ENGINE")
        key = f"{engine_type}_vector" if is_vector else engine_type

        repo_class = repository_registry.get(key)
        return repo_class(identifier)

    @abstractmethod
    async def find_by_id(self, id: Union[int, str]) -> Optional[T]: ...

    @abstractmethod
    async def find_all(self) -> List[T]: ...

    @abstractmethod
    async def create(self, data: Any) -> T: ...

    @abstractmethod
    async def create_many(self, data: List[Any]) -> List[T]: ...

    @abstractmethod
    async def update(self, id: Union[int, str], data: Any) -> Optional[T]: ...

    @abstractmethod
    async def delete(self, id: Union[int, str]) -> bool: ...


class IVectorRepository(IRepository[T], Generic[T]):
    @abstractmethod
    async def similarity_search(self, query_vector: List[float], limit: int = 5) -> List[Any]: ...
