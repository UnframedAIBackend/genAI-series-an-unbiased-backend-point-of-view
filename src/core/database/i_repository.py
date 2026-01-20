from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar, Union

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
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
