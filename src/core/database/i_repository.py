from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar, Union

from src.core.configuration.configuration import config
from src.core.database.database_engine import DatabaseEngine
from src.core.database.repository_registry import repository_registry

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    def _get_engine(self, identifier: str) -> Any:
        engine_type = config.get("DATABASE_ENGINE")

        if engine_type == DatabaseEngine.NOSQL:
            repo_class = repository_registry.get(DatabaseEngine.NOSQL)
            return repo_class(identifier)
        elif engine_type == DatabaseEngine.SQL:
            repo_class = repository_registry.get(DatabaseEngine.SQL)
            return repo_class(identifier)

        raise ValueError(f"Unsupported database engine: {engine_type}")

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
