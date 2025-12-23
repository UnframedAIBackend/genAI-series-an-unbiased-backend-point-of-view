from typing import Protocol, TypeVar, Optional, List, Any
from abc import ABC, abstractmethod

from src.database.database_engine import DatabaseEngine
from src.database.mongodb_repository import MongoDBRepository
from src.database.postgresql_repository import PostgreSQLRepository


T = TypeVar("T")

@abstractmethod
class IRepository(ABC):

    def __init__(self, identifier: str):
        self.__engines: dict[str, Type[DatabaseEngine]] = {
            DatabaseEngine.NOSQL: MongoDBRepository(identifier),
            DatabaseEngine.SQL: PostgreSQLRepository(identifier),
        }

    def _get_engine(self, engine: DatabaseEngine) -> Type[DatabaseEngine]:
        return self.__engines.get(engine)

    @abstractmethod
    async def find_by_id(self, id: int | str) -> Optional[T]: ...
    
    @abstractmethod
    async def find_all(self) -> List[T]: ...
    
    @abstractmethod
    async def create(self, data: Any) -> T: ...

    @abstractmethod
    async def create_many(self, data: List[Any]) -> List[T]: ...
    
    @abstractmethod
    async def update(self, id: int | str, data: Any) -> Optional[T]: ...
    
    @abstractmethod
    async def delete(self, id: int | str) -> bool: ...
