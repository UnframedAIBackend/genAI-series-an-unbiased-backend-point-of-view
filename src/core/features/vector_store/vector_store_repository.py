from typing import List, Optional, Type, Union

from src.core.database.i_repository import IVectorRepository
from src.core.features.vector_store.vector_store_entity import VectorEntity


class VectorStoreRepository(IVectorRepository[VectorEntity]):
    __IDENTIFIER: str = "vector_store"

    def __init__(self, repository_class: Type[IVectorRepository]):
        self.__repository = repository_class(self.__IDENTIFIER)

    async def find_by_id(self, id: Union[int, str]) -> Optional[VectorEntity]:
        return await self.__repository.find_by_id(id)

    async def find_all(self) -> List[VectorEntity]:
        return await self.__repository.find_all()

    async def create(self, data: VectorEntity) -> VectorEntity:
        return await self.__repository.create(data)

    async def create_many(self, data: List[VectorEntity]) -> List[VectorEntity]:
        return await self.__repository.create_many(data)

    async def update(self, id: Union[int, str], data: VectorEntity) -> Optional[VectorEntity]:
        return await self.__repository.update(id, data)

    async def delete(self, id: Union[int, str]) -> bool:
        return await self.__repository.delete(id)

    async def similarity_search(self, query_vector: List[float], limit: int = 5) -> List[dict]:
        return await self.__repository.similarity_search(query_vector, limit)
