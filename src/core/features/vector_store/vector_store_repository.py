from typing import List, Optional, Union

from src.core.database.i_repository import IRepository
from src.core.features.vector_store.vector_store_entity import VectorEntity


class VectorStoreRepository(IRepository[VectorEntity]):
    __IDENTIFIER: str = "vector_store"
    __repository: IRepository

    def __init__(self):
        self.__repository = self._get_engine(self.__IDENTIFIER)

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
